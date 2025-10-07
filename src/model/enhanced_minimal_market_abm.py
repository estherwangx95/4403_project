# src/model/enhanced_minimal_market_abm.py
import numpy as np
from collections import defaultdict
from src.agents.resident_agent import ResidentAgent
from src.agents.supermarket_agent import SupermarketAgent
from src.agents.group_leader_agent import GroupLeaderAgent
from src.environment.enhanced_market_environment import EnhancedMarketEnvironment
from src.metrics.complexity_metrics import ComplexityMetrics

class EnhancedMinimalMarketABM:
    """
    增强的最小市场ABM模型
    集成所有组件并实现复杂性追踪功能
    """
    
    def __init__(self, num_residents=50, has_groupbuy=True, random_seed=None):
        # 设置随机种子确保可重复性
        if random_seed is not None:
            np.random.seed(random_seed)
            
        self.num_residents = num_residents
        self.has_groupbuy = has_groupbuy
        
        # 初始化核心组件
        self.environment = EnhancedMarketEnvironment()
        self.complexity_tracker = ComplexityMetrics()
        
        # 创建智能体
        self.residents = self._create_residents()
        self.supermarket = SupermarketAgent(unique_id=0, model=self)
        self.leader = GroupLeaderAgent(unique_id=1, model=self) if has_groupbuy else None
        
        # 指标记录
        self.metrics = {
            'daily_demand': [],
            'daily_spoilage': [], 
            'daily_revenue': [],
            'customer_satisfaction': [],
            'system_complexity': []
        }
        
        # 交互历史
        self.interaction_history = []
        self.current_interactions = defaultdict(list)
        
        # 模拟状态
        self.current_day = 0
        self.is_running = True
    
    def _create_residents(self):
        """
        创建居民智能体群体
        基于ABS Census 2021数据分布
        """
        residents = []
        household_distribution = [1, 2, 2, 3, 3, 3, 4]  # 近似真实分布
        
        for i in range(self.num_residents):
            # 随机家庭规模
            household_size = np.random.choice(household_distribution)
            
            # 收入水平分布 (20%高, 50%中, 30%低)
            income_roll = np.random.random()
            if income_roll < 0.3:
                income_level = 1  # 低收入
            elif income_roll < 0.8:
                income_level = 2  # 中等收入
            else:
                income_level = 3  # 高收入
                
            # 随机位置
            location = (np.random.uniform(0, 10), np.random.uniform(0, 10))
            
            resident = ResidentAgent(
                unique_id=i+2,  # 0和1被超市和团长占用
                model=self,
                household_size=household_size,
                income_level=income_level,
                location=location
            )
            residents.append(resident)
            
        return residents
    
    def _record_interaction(self, agent_type1, agent_id1, agent_type2, agent_id2, interaction_type):
        """
        记录智能体间交互
        """
        interaction_key = f"{agent_type1}_{agent_id1}_{agent_type2}_{agent_id2}"
        self.current_interactions[interaction_key].append({
            'type': interaction_type,
            'day': self.current_day
        })
    
    def run_one_day(self):
        """
        运行一天模拟
        """
        daily_metrics = {
            'total_demand': 0,
            'total_spoilage': 0,
            'total_revenue': 0,
            'avg_satisfaction': 0,
            'groupbuy_volume': 0
        }
        
        # 重置当日交互记录
        self.current_interactions = defaultdict(list)
        
        # 居民决策阶段
        satisfaction_sum = 0
        for resident in self.residents:
            resident.step()
            
            # 居民购买决策
            purchase_result = resident.make_purchase_decision(
                supermarket_price=self.supermarket.base_price,
                groupbuy_price=self.leader.negotiated_price if self.leader else None
            )
            
            # 记录交互
            if purchase_result == "supermarket":
                self._record_interaction('resident', resident.unique_id, 'supermarket', 0, 'purchase')
                daily_metrics['total_demand'] += resident.calculate_demand()
            elif purchase_result == "groupbuy" and self.leader:
                self._record_interaction('resident', resident.unique_id, 'leader', 1, 'group_purchase')
            
            satisfaction_sum += resident.satisfaction_level
        
        # 团长活动（如果存在）
        if self.leader:
            self.leader.step()
            if hasattr(self.leader, 'total_volume_organized'):
                daily_metrics['groupbuy_volume'] = self.leader.total_volume_organized
        
        # 超市运营
        self.supermarket.step()
        daily_metrics['total_spoilage'] = self.supermarket.total_spoilage
        daily_metrics['total_revenue'] = self.supermarket.revenue
        daily_metrics['avg_satisfaction'] = satisfaction_sum / len(self.residents)
        
        # 记录基础指标
        self.metrics['daily_demand'].append(daily_metrics['total_demand'])
        self.metrics['daily_spoilage'].append(daily_metrics['total_spoilage'])
        self.metrics['daily_revenue'].append(daily_metrics['total_revenue'])
        self.metrics['customer_satisfaction'].append(daily_metrics['avg_satisfaction'])
        
        # 更新复杂性指标
        self._update_complexity_metrics()
        
        # 环境推进
        self.environment.advance_day()
        self.current_day += 1
        
        # 将复杂性指标加入返回结果
        daily_metrics['complexity'] = self.get_daily_complexity()
        
        return daily_metrics
    
    def _update_complexity_metrics(self):
        """
        更新复杂性度量指标
        """
        # 构建交互矩阵
        interaction_matrix = self._build_interaction_matrix()
        
        # 更新复杂性追踪器
        self.complexity_tracker.update_all_metrics(
            demand_series=self.metrics['daily_demand'],
            spoilage_series=self.metrics['daily_spoilage'],
            interaction_matrix=interaction_matrix
        )
        
        # 记录复杂性指标
        current_complexity = self.complexity_tracker.get_current_metrics()
        self.metrics['system_complexity'].append(current_complexity)
        
        # 保存交互历史
        self.interaction_history.append(dict(self.current_interactions))
    
    def _build_interaction_matrix(self):
        """
        构建交互矩阵用于网络分析
        """
        n_agents = len(self.residents) + 2  # 居民 + 超市 + 团长
        matrix = np.zeros((n_agents, n_agents))
        
        # 简化处理：每个居民都与超市有基础交互
        for i in range(len(self.residents)):
            matrix[i, len(self.residents)] = 1  # 居民->超市
            matrix[len(self.residents), i] = 1  # 超市->居民
            
        # 如果有团长，记录团长交互
        if self.leader:
            leader_idx = len(self.residents) + 1
            # 团长与超市交互
            matrix[leader_idx, len(self.residents)] = 1
            matrix[len(self.residents), leader_idx] = 1
            
            # 团长与居民交互（简化：假设与所有居民交互）
            for i in range(len(self.residents)):
                matrix[i, leader_idx] = 1
                matrix[leader_idx, i] = 1
        
        return matrix
    
    def get_daily_complexity(self):
        """
        获取当日复杂性指标
        """
        return self.complexity_tracker.get_current_metrics()
    
    def run_simulation(self, days=90):
        """
        运行多天模拟
        """
        results = []
        
        for day in range(days):
            if not self.is_running:
                break
                
            daily_result = self.run_one_day()
            daily_result['day'] = day
            results.append(daily_result)
            
            # 可选：每30天应用随机冲击
            if day > 0 and day % 30 == 0 and np.random.random() < 0.3:
                shock_type = np.random.choice(['demand_spike', 'supply_chain_disruption'])
                self.environment.apply_external_shock(shock_type, magnitude=0.3)
        
        return results
    
    def get_final_metrics(self):
        """
        获取模拟结束后的汇总指标
        """
        return {
            'total_days': self.current_day,
            'avg_daily_demand': np.mean(self.metrics['daily_demand']),
            'avg_daily_spoilage': np.mean(self.metrics['daily_spoilage']),
            'total_revenue': np.sum(self.metrics['daily_revenue']),
            'final_complexity': self.get_daily_complexity(),
            'complexity_trend': self._calculate_complexity_trend()
        }
    
    def _calculate_complexity_trend(self):
        """
        计算复杂性指标的变化趋势
        """
        if len(self.metrics['system_complexity']) < 10:
            return {}
            
        recent = self.metrics['system_complexity'][-10:]
        early = self.metrics['system_complexity'][:10]
        
        trends = {}
        for metric in ['entropy', 'network_density', 'cv']:
            recent_avg = np.mean([c[metric] for c in recent if metric in c])
            early_avg = np.mean([c[metric] for c in early if metric in c])
            trends[metric] = recent_avg - early_avg
            
        return trends
