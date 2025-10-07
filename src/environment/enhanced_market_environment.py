# src/environment/enhanced_market_environment.py
import numpy as np
from datetime import datetime

class EnhancedMarketEnvironment:
    """
    增强市场环境类
    管理模拟环境的状态、季节效应和系统级属性
    """
    
    def __init__(self, start_date=None):
        # 时间管理
        self.current_date = start_date or datetime(2023, 1, 1)
        self.day_of_year = 1
        
        # 环境参数
        self.seasonal_factors = {
            'summer': 1.3,  # 夏季损耗乘数
            'spring': 1.0,
            'autumn': 0.9,
            'winter': 0.7   # 冬季损耗乘数
        }
        
        # 系统状态记录
        self.demand_history = []
        self.spoilage_history = []
        self.price_history = []
        self.interaction_matrices = []  # 存储每日交互矩阵
        
        # 外部冲击模拟
        self.external_shocks = {
            'supply_chain_disruption': False,
            'demand_spike': False,
            'weather_event': False
        }
    
    def get_seasonal_factor(self):
        """
        根据日期计算季节性因子
        理论依据：FAO食物浪费报告中的季节模式
        """
        day_of_year = self.day_of_year
        
        if 80 <= day_of_year <= 172:  # 春季
            return self.seasonal_factors['spring']
        elif 173 <= day_of_year <= 265:  # 夏季
            return self.seasonal_factors['summer']
        elif 266 <= day_of_year <= 355:  # 秋季
            return self.seasonal_factors['autumn']
        else:  # 冬季
            return self.seasonal_factors['winter']
    
    def apply_external_shock(self, shock_type, magnitude=0.5, duration=7):
        """
        应用外部冲击模拟现实世界事件
        """
        self.external_shocks[shock_type] = {
            'magnitude': magnitude,
            'duration': duration,
            'start_day': self.day_of_year
        }
    
    def update_shocks(self):
        """
        更新外部冲击状态
        """
        for shock_type, shock_info in self.external_shocks.items():
            if shock_info and isinstance(shock_info, dict):
                elapsed_days = self.day_of_year - shock_info['start_day']
                if elapsed_days >= shock_info['duration']:
                    self.external_shocks[shock_type] = False
    
    def get_demand_multiplier(self):
        """
        获取需求乘数（考虑外部冲击）
        """
        multiplier = 1.0
        
        if self.external_shocks['demand_spike']:
            multiplier += self.external_shocks['demand_spike']['magnitude']
            
        if self.external_shocks['supply_chain_disruption']:
            multiplier -= self.external_shocks['supply_chain_disruption']['magnitude'] * 0.5
            
        return max(0.1, multiplier)  # 确保最小值
    
    def record_daily_data(self, daily_demand, daily_spoilage, avg_price, interactions):
        """
        记录每日系统数据
        """
        self.demand_history.append(daily_demand)
        self.spoilage_history.append(daily_spoilage)
        self.price_history.append(avg_price)
        self.interaction_matrices.append(interactions)
    
    def advance_day(self):
        """
        推进到下一天
        """
        self.current_date = datetime(
            self.current_date.year, 
            self.current_date.month, 
            self.current_date.day
        ) + timedelta(days=1)
        
        self.day_of_year = self.current_date.timetuple().tm_yday
        self.update_shocks()
    
    def get_system_state_summary(self):
        """
        获取系统状态摘要
        """
        recent_demand = self.demand_history[-10:] if self.demand_history else [0]
        recent_spoilage = self.spoilage_history[-10:] if self.spoilage_history else [0]
        
        return {
            'current_date': self.current_date,
            'season': self.get_season_name(),
            'demand_trend': np.mean(np.diff(recent_demand)) if len(recent_demand) > 1 else 0,
            'spoilage_trend': np.mean(np.diff(recent_spoilage)) if len(recent_spoilage) > 1 else 0,
            'active_shocks': sum(1 for shock in self.external_shocks.values() if shock)
        }
    
    def get_season_name(self):
        """
        获取当前季节名称
        """
        day = self.day_of_year
        if 80 <= day <= 172:
            return "Spring"
        elif 173 <= day <= 265:
            return "Summer"
        elif 266 <= day <= 355:
            return "Autumn"
        else:
            return "Winter"
