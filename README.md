# 🧩 Community Group Buying ABM Simulation

## 1. Overview

This project presents an **Agent-Based Model (ABM)** simulation of community group buying — a social retail phenomenon in which local leaders organize community members to purchase fresh goods through online platforms.  

The model explores how **social trust diffusion**, **leader influence**, and **platform subsidies** interact to shape adoption dynamics and market equilibrium.  

The simulation is implemented in Python, using a modular design that supports visualization, sensitivity testing, and dynamic feedback analysis.

---

## 2. Model Design

### 2.1 Agent Types and Roles

| Agent Type | Real-world Role | Model Function | Decision Level |
|-------------|----------------|----------------|----------------|
| **Consumer** | Individual community residents | Decide whether to buy based on trust and price sensitivity | Micro |
| **Leader** | Community group organizer | Influence nearby consumers through reputation and social connections | Meso |
| **Platform** | E-commerce platform (e.g., Meituan Youxuan) | Adjust subsidy levels dynamically based on total sales | Macro |

---

### 2.2 Agent Attributes

#### (1) Consumer
| Variable | Description | Range |
|-----------|--------------|--------|
| `trust` | Trust level toward leader/platform | [0, 1] |
| `price_sensitivity` | How sensitive the consumer is to price | [0.3, 2.0] |
| `network` | Neighbor list (social connections) | List[int] |
| `purchased` | Whether the consumer purchased this step | Boolean |

#### (2) Leader
| Variable | Description | Range |
|-----------|--------------|--------|
| `reputation` | Leader’s credibility and influence | [0.5, 1.0] |
| `connections` | List of consumers influenced | List[int] |
| `influence` | Derived influence strength | Dynamic |

#### (3) Platform
| Variable | Description | Range |
|-----------|--------------|--------|
| `base_price` | Base product price | Float |
| `subsidy` | Dynamic subsidy per product | Float |
| `sales_record` | Historical sales data | List[int] |

---

### 2.3 Behavioral Rules

#### Consumer Behavior
Each consumer decides to purchase according to:
\[
P(\text{buy}) = \frac{trust \times influence}{0.5 + price\_sensitivity}
\]
If `random.random() < P`, the consumer purchases.

Trust is diffused through social ties:
\[
trust_{neighbor} = trust_{neighbor} + \Delta (1 - trust_{neighbor})
\]
where Δ is the trust diffusion rate (typically 0.05–0.1).

#### Leader Behavior
Leaders promote products and influence consumers:
\[
influence = 0.5 + 0.5 \times reputation
\]

#### Platform Behavior
The platform adjusts subsidy based on sales:
```python
if sales < 0.3 * config.N_CONSUMERS:
            self.subsidy += 0.2