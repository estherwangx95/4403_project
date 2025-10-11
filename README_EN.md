🧩 Agent Design Specification

1. Overview

This agent-based model (ABM) simulates the dynamics of community group buying —
a socio-economic phenomenon where consumers purchase fresh produce collectively through local leaders under the coordination of an online platform.

The model consists of three primary types of agents, each representing different levels of decision-making within the system:
Consumers, Leaders, and Platform.
Their interactions form a bottom-up dynamic process in which social trust and platform incentives jointly drive market participation.

⸻

2. Agent Types and Roles

Agent Type	Representation in Reality	Role in Model	Decision Level
🧍‍♀️ Consumer	Individual residents in a community	Make purchasing decisions based on trust and price sensitivity	Micro-level
👑 Leader	Community group buying organizers	Promote products and influence consumer behavior through reputation	Meso-level
🏦 Platform	The digital platform (e.g., Meituan Youxuan, Xingsheng Youxuan)	Adjust subsidy and pricing strategies based on total sales	Macro-level


⸻

3. Agent Attributes (State Variables)

(1) Consumer Agent

Variable	Description	Value Range / Type
trust	Degree of trust toward leader or platform; determines susceptibility to influence	[0, 1] (float)
price_sensitivity	Sensitivity to price or subsidy changes; higher means less likely to purchase	[0.3, 2.0] (float)
network	Set of connected consumers (social neighbors)	List[int]
purchased	Whether the consumer made a purchase in the current time step	Boolean


⸻

(2) Leader Agent

Variable	Description	Value Range / Type
reputation	The leader’s perceived reliability or charisma	[0.5, 1.0] (float)
connections	List of consumers directly influenced by the leader	List[int]
influence	Promotional influence strength determined by leader reputation	Computed each step


⸻

(3) Platform Agent

Variable	Description	Value Range / Type
base_price	Baseline product price offered by the platform	Float
subsidy	Dynamic subsidy level adjusted in response to sales	Float
sales_record	Cumulative sales volume across time steps	List[int]


⸻

4. Agent Behavior Rules

(1) Consumer Behavior
	•	Receive Influence:
Each consumer receives promotional signals from connected leaders.
A probability of purchase p is calculated as:
p = \frac{trust \times influence}{0.5 + price\_sensitivity}
If random.random() < p, the consumer purchases the product.
	•	Word-of-Mouth Diffusion:
Consumers who purchased transmit trust to their neighbors:
trust_{neighbor} = trust_{neighbor} + \Delta (1 - trust_{neighbor})
where \Delta is a small diffusion constant (e.g., 0.05–0.1).

⸻

(2) Leader Behavior
	•	Promotion:
Each leader promotes products to connected consumers with influence proportional to reputation:
influence = 0.5 + 0.5 \times reputation
	•	Leaders do not directly purchase but act as information transmitters.

⸻

(3) Platform Behavior
	•	Subsidy Adjustment:
The platform observes the total number of purchases each step and adapts subsidy accordingly:

if sales > 10:
    subsidy *= 0.95
else:
    subsidy *= 1.05


	•	Feedback Loop:
Lower subsidies reduce purchase probability, forming a closed-loop adaptive mechanism that balances market demand and platform cost.

⸻

5. Agent Interactions

Interaction Type	Source Agent	Target Agent	Description
Promotion	Leader	Consumer	Leader sends promotional signals based on reputation
Purchase Decision	Consumer	—	Consumer decides whether to buy according to trust and price sensitivity
Word-of-Mouth	Consumer	Consumer	Purchased consumers increase neighbors’ trust
Subsidy Feedback	Platform	All Agents	Platform adjusts subsidy based on sales outcome


⸻

6. Scheduling and Temporal Structure

The simulation proceeds in discrete time steps (e.g., 30).
At each step:
	1.	Leaders promote products to their connected consumers.
	2.	Consumers decide whether to purchase.
	3.	Word-of-mouth trust diffusion occurs among consumers.
	4.	Platform observes total sales and updates the subsidy.
	5.	All agents reset short-term purchase flags.

This update mechanism is implemented through a custom scheduler (SocialScheduler) that governs inter-agent interactions in the correct causal order.

⸻

7. Conceptual Model Summary

The overall agent interaction structure can be visualized as:

Platform  →  Leader  →  Consumer  ↔  Consumer
   ↑                                 ↓
   └─────────── Feedback (sales) ────┘

This reflects a multi-level adaptive system:
	•	Micro-level: Consumers make local, probabilistic decisions.
	•	Meso-level: Leaders amplify influence and propagate information.
	•	Macro-level: The platform regulates economic incentives based on aggregate outcomes.

⸻

8. Key Design Principles
	•	Autonomy: Each agent makes independent decisions based on local states.
	•	Heterogeneity: Consumers differ in trust and price sensitivity.
	•	Adaptivity: Platform dynamically responds to collective outcomes.
	•	Emergence: Aggregate market behavior (sales trends) emerges from local interactions.

⸻

✅ Summary Table

Agent Type	Key Variables	Key Behaviors	Interaction Targets
Consumer	trust, price_sensitivity, network, purchased	Receive influence, purchase, spread trust	Leader, Consumer
Leader	reputation, connections	Promote products	Consumer
Platform	base_price, subsidy	Adjust subsidy, observe sales	Leader, Consumer


⸻

9. Model Scope
	•	Agents: 1 platform, 3–10 leaders, 50–100 consumers
	•	Simulation Steps: 30 time periods
	•	Output Metrics: total sales, average trust, platform subsidy evolution
	•	Purpose: to analyze how trust and economic incentives co-evolve in community group buying ecosystems.

⸻

✅ In summary:

The ABM framework models the interplay between social trust diffusion and platform-level economic feedback.
Through autonomous agent behaviors and adaptive subsidy control, the model captures realistic emergent phenomena observed in community-based retail systems.

⸻

是否希望我下一步帮你写出这一节之后的下一部分 ——
📊 “Model Dynamics and Simulation Workflow” (模型运行与时间更新机制)？
它会说明 scheduler + step-by-step update 的顺序（用于报告 Methodology Section）。


trust_diffusion_dualview
左侧（网络动态图）
	•	节点颜色由冷→暖：表示信任逐步增强；
	•	方形节点为团长（leaders）；
	•	信任通过连接边逐步扩散；
	•	越靠中心的节点信任增长越快。

右侧（信任曲线）
	•	折线从下向上平滑上升；
	•	表示系统平均信任度随时间的增长；
	•	到达稳定后趋于平稳，符合社会扩散模型逻辑。
The dual-view animation visualizes both micro-level interactions and macro-level trust evolution.
Leader nodes (squares) initiate influence cascades, while consumers progressively build trust through social reinforcement.
The right-hand curve confirms the system’s self-reinforcing property: as social trust grows, further adoption becomes increasingly likely.