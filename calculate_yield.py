# calculate_yield.py
from parameters import initial_deposit, deposit_apy, borrow_apy, ltv, cycles, days, swap_slippage, liquidation_threshold

def calculate_max_yield(P, deposit_apy, borrow_apy, ltv, cycles, days, swap_slippage, liquidation_threshold):
    results = []

    # 將 APY 轉換為日利率
    deposit_daily_rate = (1 + deposit_apy)**(1/365) - 1
    borrow_daily_rate = (1 + borrow_apy)**(1/365) - 1
    
    for i in range(1, cycles + 1):
        total_deposit = P
        total_borrow = 0
        
        for _ in range(i):
            borrow_amount = total_deposit * ltv
            swap_amount = borrow_amount * (1 - swap_slippage)  # 考慮 Swap 磨耗
            total_deposit += swap_amount
            total_borrow += borrow_amount
        
        total_deposit = P * (1 - (ltv * (1 - swap_slippage))**(i + 1)) / (1 - ltv * (1 - swap_slippage))  # 根據循環次數計算總存款
        total_borrow = total_deposit - P  # 總借款為總存款減去初始存款

        # 計算 365 天的收益
        total_deposit_after_year = total_deposit * ((1 + deposit_daily_rate) ** 365)
        total_borrow_after_year = total_borrow * ((1 + borrow_daily_rate) ** 365)

        profit = total_deposit_after_year - total_deposit
        cost = total_borrow_after_year - total_borrow

        net_yield = profit - cost
        total_apy = (net_yield / P) * 100  # 將收益率轉換為年化百分比形式

        # 計算實際運行天數的預期收益
        total_deposit_after_days = total_deposit * ((1 + deposit_daily_rate) ** days)
        total_borrow_after_days = total_borrow * ((1 + borrow_daily_rate) ** days)

        actual_profit = total_deposit_after_days - total_deposit
        actual_cost = total_borrow_after_days - total_borrow

        actual_net_yield = actual_profit - actual_cost

        results.append((i, total_apy, actual_net_yield))

    return results

def calculate_liquidation_time(initial_borrow, borrow_apy, liquidation_threshold):
    borrow_daily_rate = (1 + borrow_apy)**(1/365) - 1
    days_to_liquidation = 0
    current_borrow = initial_borrow

    while current_borrow / initial_deposit < liquidation_threshold:
        current_borrow *= (1 + borrow_daily_rate)
        days_to_liquidation += 1

    return days_to_liquidation

# # 用戶輸入參數
# initial_deposit = 30000  # 初始存款
# deposit_apy = 0.185  # 存款 APY
# borrow_apy = 0.06  # 借款 APY
# ltv = 0.8  # 借款 LTV
# cycles = 10  # 循環次數
# days = 60  # 運行天數
# swap_slippage = 0.001  # Swap 磨耗，預設為 0.1%
# liquidation_threshold = 0.85  # 清算閾值

# 計算最高收益
results = calculate_max_yield(initial_deposit, deposit_apy, borrow_apy, ltv, cycles, days, swap_slippage, liquidation_threshold)

# 計算清算時間
initial_borrow = initial_deposit * ltv
days_to_liquidation = calculate_liquidation_time(initial_borrow, borrow_apy, liquidation_threshold)

# 打印結果
for cycle, total_apy, actual_net_yield in results:
    print(f"[循環 {cycle} 次] Total APY：{total_apy:.2f}%，運行 {days} 天後預期收益為：{actual_net_yield:.2f} u")

print(f"根據目前的借款 APY 和 LTV，距離清算閾值 {liquidation_threshold} 大約需要：{days_to_liquidation} 天")
