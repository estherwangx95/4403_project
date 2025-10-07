# src/metrics/complexity_metrics.py
import numpy as np
from scipy import stats
import numpy as np

class ComplexityMetrics:
    """
    复杂性度量类
    实现复杂系统理论中的多种度量指标，用于量化系统行为
    """
    
    def __init__(self):
        # 历史指标记录
        self.metrics_history = {
            'entropy': [],           # 系统熵
            'network_density': [],   # 网络密度
            'cv': [],               # 变异系数
            'hurst_exponent': [],    # 赫斯特指数
            'lyapunov_estimate': []  # 李雅普诺夫指数估计
        }
        
    def calculate_entropy(self, data_series):
        """
        计算时间序列的香农熵
        理论依据：信息论，衡量系统不确定性
        """
        if len(data_series) < 2:
            return 0
            
        # 创建概率分布
        hist, bin_edges = np.histogram(data_series, bins=10, density=True)
        hist = hist[hist > 0]  # 移除零概率
        
        if len(hist) == 0:
            return 0
            
        # 计算香农熵
        entropy = -np.sum(hist * np.log2(hist))
        return entropy
    
    def calculate_network_density(self, interaction_matrix):
        """
        计算交互网络密度
        理论依据：图论，衡量系统连接性
        """
        if interaction_matrix.size == 0:
            return 0
            
        n = len(interaction_matrix)
        if n <= 1:
            return 0
            
        # 计算实际连接数与可能连接数的比例
        actual_connections = np.sum(interaction_matrix > 0)
        possible_connections = n * (n - 1)
        
        return actual_connections / possible_connections if possible_connections > 0 else 0
    
    def calculate_variation_coefficient(self, data_series):
        """
        计算变异系数 (Coefficient of Variation)
        理论依据：统计学，衡量相对波动性
        """
        if len(data_series) < 2 or np.mean(data_series) == 0:
            return 0
            
        return np.std(data_series) / np.mean(data_series)
    
    def estimate_hurst_exponent(self, time_series):
        """
        估计赫斯特指数
        理论依据：分形分析，衡量时间序列的长程依赖性
        - H < 0.5: 均值回归
        - H = 0.5: 随机游走  
        - H > 0.5: 趋势持续
        """
        if len(time_series) < 20:
            return 0.5
            
        try:
            # 简化版本的R/S分析
            lags = range(2, min(20, len(time_series)//2))
            tau = []
            
            for lag in lags:
                if lag >= len(time_series):
                    continue
                # 计算滞后差值的标准差
                diff_std = np.std(np.subtract(time_series[lag:], time_series[:-lag]))
                tau.append(diff_std)
            
            if len(tau) < 2:
                return 0.5
                
            # 线性回归计算赫斯特指数
            poly = np.polyfit(np.log(list(lags)[:len(tau)]), np.log(tau), 1)
            return poly[0]
            
        except Exception as e:
            print(f"赫斯特指数计算错误: {e}")
            return 0.5
    
    def estimate_lyapunov_exponent(self, time_series):
        """
        估计李雅普诺夫指数
        理论依据：混沌理论，衡量系统对初始条件的敏感性
        """
        if len(time_series) < 20:
            return 0
            
        try:
            differences = []
            max_lag = min(10, len(time_series)//2)
            
            for i in range(1, max_lag):
                if i >= len(time_series):
                    continue
                # 计算不同时间滞后的差异
                diff = np.abs(time_series[i:] - time_series[:-i])
                differences.append(np.mean(diff))
            
            if len(differences) < 2:
                return 0
                
            # 线性拟合斜率作为李雅普诺夫指数估计
            x = np.arange(1, len(differences) + 1)
            slope, _ = np.polyfit(x, np.log(np.array(differences) + 1e-10), 1)
            return slope
            
        except Exception as e:
            print(f"李雅普诺夫指数计算错误: {e}")
            return 0
    
    def update_all_metrics(self, demand_series, spoilage_series, interaction_matrix):
        """
        更新所有复杂性指标
        """
        # 合并需求与损耗序列作为系统状态指标
        combined_series = np.array(demand_series) + np.array(spoilage_series)
        
        # 计算并记录各项指标
        self.metrics_history['entropy'].append(
            self.calculate_entropy(combined_series)
        )
        
        self.metrics_history['network_density'].append(
            self.calculate_network_density(interaction_matrix)
        )
        
        self.metrics_history['cv'].append(
            self.calculate_variation_coefficient(combined_series)
        )
        
        self.metrics_history['hurst_exponent'].append(
            self.estimate_hurst_exponent(combined_series)
        )
        
        self.metrics_history['lyapunov_estimate'].append(
            self.estimate_lyapunov_exponent(combined_series)
        )
    
    def get_current_metrics(self):
        """
        获取当前所有指标的最新值
        """
        return {
            metric: values[-1] if values else 0
            for metric, values in self.metrics_history.items()
        }
