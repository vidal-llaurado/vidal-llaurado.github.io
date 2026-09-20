# On modeling compute markets

*Modeling delivery curves against an operating balance sheet*

A GPU fleet earns rent, promises service and supports debt. Each claim draws on the same machines, but each values a different right. A useful compute model must explain how those values move together without treating them as interchangeable.

The distinction is becoming tradable. In August 2026, CME Group and Silicon Data announced H100 and B200 rental-index futures for October 5, pending regulatory review.[^1] In September, Reuters reported a $22 billion loan to Crux AI, backed by chips and customer contracts.[^2] A rental benchmark, a delivery promise and a lender’s collateral now meet on the same balance sheet. The benchmark alone cannot price the other two.

I model that connection as a family of stochastic delivery curves coupled to an operator’s capacity, commitments, cash and debt. The curves describe the market across delivery dates. The balance sheet determines which promises an operator can afford to make. Their interaction is where a financial reference becomes a commercial price.

## The unit is a service obligation

A GPU lasts; its available hours expire. A queue carries unfinished work into tomorrow, but today’s unused capacity cannot follow it. That rules out the storage trade that connects spot and forward prices for an inventory commodity. Ownership, scheduling and investment still connect delivery dates, as operating constraints do in electricity markets.[^3]

The unit also has a shape. Sixty-four GPUs in one suitable cluster are not equivalent to the same GPU-hours scattered across locations and dates. Memory, networking, software, interruption rights and latency belong in the service definition. MLPerf’s workload, quality and performance conditions illustrate why a hardware label cannot substitute for a specification.[^4]

Contracts can sell hardware time or useful work. Hardware time is schedulable; useful output depends on the workload and the conditions under which it counts. Both need a benchmark, and both retain *basis risk*: the difference between the benchmark exposure and the service actually owed. Aggregating hours before checking compatibility can make a physically impossible book look balanced.

Reserving capacity and hedging its price therefore require different contracts. AWS Capacity Blocks fix the reservation price at purchase and charge it upfront.[^5] A rental-index future transfers benchmark price exposure. Owning that exposure supplies neither a cluster nor the cash needed to procure one.

The model distinguishes an observed index, an executable offer, a physical forecast, a financial forward and a reservation price for a particular book. For a clean forward with one terminal settlement, zero initial value implies

$$
F_t^{\mathrm{fwd}}(T)
=\frac{\mathbb E_t^{\mathbb P}[M_{t,T}S_T]}
{\mathbb E_t^{\mathbb P}[M_{t,T}]}.
$$

The stochastic discount factor $M_{t,T}$ values dollars across dates and states. In an incomplete market, traded claims need not determine it for every regional, technological or contractual exposure. Market consistency constrains the extension; it does not make the extension unique. Nor is this terminal forward automatically equal to a futures price whose gains and losses settle along the way.

## Delivery dates belong in the state

An operator may rent capacity next week, guarantee it for a year and finance equipment over five. Those commitments load different parts of the curve. Modeling only spot prices leaves the term structure to be reconstructed, with its assumptions hidden in that second step.

The market object is a family of curves,

$$
F_t^j(T)=\mathcal F_j(t,T;X_t),
$$

where $j$ denotes a reference service, $T$ a delivery date and $X_t$ the shared stochastic state. HJM supplies the term-structure precedent; commodity extensions account for common shocks and delivery periods.[^6][^7] Here the clean futures references obey their pricing-law restrictions, while physical contracts add delivery rights and obligations.

A temporary shortage can lift the front of the curve without moving its distant end. New supply can depress future margins while today’s scarcity persists. A generation transition can move one hardware class against another. A single “GPU price” loses precisely the shape that matters to a lender assessing several years of collateral support.

Calendar roll must also be explicit. Musiela coordinates write $f_t^j(x)=F_t^j(t+x)$, with $x$ denoting time to delivery. As time passes, the transport term shifts the curve through these coordinates; it does not remove ageing or force a fixed-delivery contract’s price to change.[^8]

A small factor state can represent market level, near-term scarcity, generation and regional basis. Its loadings determine which delivery dates each shock reaches. Power, rates and commercial funding conditions share relevant shocks with compute, so operating margins, discounting and borrowing capacity can deteriorate together. Sharing a state does not make the commercial funding curve a traded asset.

That state carries two laws. Under $\mathbb P$, the operator forecasts and plans. Under $\mathbb Q$, clean claims satisfy the chosen pricing restrictions. Risk premia connect the laws without identifying a forecast with a forward price.[^7] Scenario trees and Monte Carlo are numerical methods for this system. They should disagree only for reasons that can be traced to their different approximations and decision problems.

Delivery periods need the same discipline. A month of service is a quantity-weighted strip of dated deliveries. Its aggregation must reproduce those components when rights and settlement dates agree. A geometric average or an unnoticed payment-date change creates a different contract. The curve is useful because it makes that difference explicit, before it reaches the valuation.

## A hedge is a position plus its residual

“Long compute” can mean floating revenue on one generation, fixed-price obligations on another, local power purchases and equipment pledged against long-dated earnings. A short rental-index future offsets only part of that book.

Locally, the hedged value changes as

$$
\Delta V_{\mathrm{hedged}}
\approx (g+H^\top q)^\top\Delta X,
$$

where $g$ is the portfolio’s factor sensitivity, the rows of $H$ are instrument sensitivities and $q$ holds the hedge positions. The residual $g+H^\top q$ states what the instruments leave exposed. A covariance-weighted projection measures its importance; position limits, market depth and available collateral determine which offsets are feasible.

A benchmark hedge can leave regional basis. A power hedge can fix a price while leaving consumption uncertain. One maturity rarely spans a curve’s level and slope independently. Delivery-bucket sensitivities translate these factor exposures back into the dates the commercial desk sells, and bucket shocks test shapes outside the fitted factor span. Zero factor residual is a statement about the chosen span, not proof that the book is safe.

Large moves require revaluation with decisions included. Customers change what they buy, operators change what they run, and lenders revise eligible collateral. Options curve the payoff; a financing threshold can change which operating policies remain feasible. A delta computed before that threshold cannot explain the business after it.

Cash timing can defeat an otherwise sensible hedge. A short futures position pays variation margin as rental prices rise, while higher operating receipts may arrive later.[^9] The eventual offset cannot fund today’s call. If trading depth and funding also deteriorate together, even a desirable hedge may be too expensive to maintain.[^10]

Substitution rights, workload migration, scheduling latitude and backup procurement reduce the risk left for financial instruments. They also have costs and limits. The dispatch desk and the trading desk must choose against the same cash budget; otherwise each can spend liquidity that the other has already used.

The instrument’s cash mechanics matter as much as its payoff. A funded put consumes its premium at purchase; a future requires cash as its mark changes. A transferable fixed-strike forward keeps its original strike, with any transfer paid at the current value. Replacing these conventions with a terminal payoff matrix can preserve reported profit while inventing the liquidity that makes it attainable.

## The payment changes the price

A fleet has three relevant values: its earning value under the owner’s operating choices, the lender’s eligible appraisal and the proceeds of an executable sale. Common curve shocks affect all three, but they answer different questions. Equipment can be worth keeping, support little borrowing and fetch still less in a hurried sale.

Contract terms consume operating options. A firm reservation ties up capacity; an interruptible agreement preserves some discretion; approved hardware substitution lets the operator choose how to deliver. Identical expected GPU-hours can therefore have different opportunity costs. Two suppliers observing the same market curve can quote different prices because their existing obligations, fragmentation and cash needs differ.

Portfolio-dependent valuation has a precedent in incomplete energy markets, where structured claims and their hedges are valued together.[^11] With explicit delivery and financing constraints, the supplier’s reservation payment becomes

$$
A^{\min}(c\mid s)
=\inf\{A:V(\Phi(s;c,A))\ge V(s)\},
$$

over feasible policies. The state $s$ includes the existing book, capacity, cash and debt. Accepting contract $c$ and payment $A$ transforms it through $\Phi$; $V$ is the optimized, risk-adjusted business value. The payment must leave the supplier at least as well off after reorganizing operations and hedges. Competition determines how far the eventual quote sits above that floor.

Crucially, payment enters the state. An upfront receipt may finance delivery or prevent a forced sale. The same nominal receipt after delivery cannot do either. Applying a funding spread after a cash-independent valuation misses this change in the feasible business. The customer is buying service and, through payment timing, may also be supplying finance.

Consider a fleet with appraisal-linked borrowing. A fall in long-dated margins lowers collateral support. Selling pledged machines raises cash but removes collateral and future earning capacity, potentially requiring another sale. Whether the shock demands cash immediately, restricts new draws or appears at refinancing depends on the agreement. Those dates and triggers belong in the model, not in a generic leverage adjustment.

Leverage therefore has no universal sign in a quote. A constrained supplier may accept less for reliable upfront cash and demand more for a deferred obligation. What matters is how the proposed contract changes the constraint that is actually binding. A price can be attractive in expected-value terms and still leave the supplier unable to survive its payment schedule.

## What can be learned from a thin market

Sparse data can support a smooth fitted curve without supporting a precise price. Transactions, executable offers, inferred marks and hand-set stresses need separate provenance and uncertainty. Treating them as equivalent observations manufactures confidence before estimation begins.

Current clean prices constrain the initial surface. Historical observations inform physical dynamics; derivative prices constrain the pricing law jointly with volatility and risk-premium assumptions. Physical reservations carry additional rights and payment terms. Pooling these indiscriminately turns contractual differences into apparent market movements.

Identification must be assessed before regularization. Several parameter combinations may explain the available prices equally well while implying different option values and hedge requirements. More simulation paths sharpen each conditional answer; they cannot choose between observationally indistinguishable models. Report that range alongside process risk so a treasury decision retains the uncertainty on which it depends.

The accompanying [implementation](https://github.com/vidal-llaurado/compute-market-model) uses synthetic inputs. Its pricing identities, held-out policy evaluations, stress experiments and calibration recovery test different parts of the construction. They establish internal consistency and measured numerical performance under stated assumptions. They do not establish that the chosen factors or financing rules describe a live operator. Real quotes, operating records and financing terms are the next identifying inputs.

Numerical evidence also needs a declared question. Refining scenario support tests a sampled valuation; evaluating a frozen policy on independent paths tests its performance; comparison with a perfect-information policy measures the cost of acting without foresight. None of these replaces the others. A solver certificate can establish an optimum for a finite program while leaving both model error and the approximation to the operating problem unresolved.

The commercial opportunity is partly contractual. A customer needing a result by Friday, with no need for a particular GPU on Tuesday, can sell scheduling flexibility. A supplier can price approved substitution. A buyer can separate benchmark protection from firm delivery. Each term should move a named exposure to the party better able to carry it, with the price reflecting the discretion transferred.

Useful-work contracts extend that idea if output and quality are defined tightly enough. Suppliers then compete on production efficiency, while the benchmark must remain meaningful as models and software change. Standardization is valuable when it makes obligations comparable; it becomes misleading when it erases the conditions that determine whether they can be met.

A compute market needs a common price language without requiring a common balance sheet. Delivery curves provide the first. Coupling them to operations and finance explains the second: what an operator can deliver, what it can hedge, and what it must be paid to carry the rest.

## References

[^1]: CME Group (2026). [CME Group and Silicon Data to Launch Compute Futures on October 5](https://www.cmegroup.com/media-room/press-releases/2026/8/11/cme_group_and_silicondatatolaunchcomputefuturesonoctober5tounloc.html).
[^2]: Reuters (2026). [Banks provide $22 billion chip loan to Blackstone, Alphabet AI cloud venture](https://www.reuters.com/world/asia-pacific/banks-provide-22-billion-chip-loan-blackstone-alphabet-cloud-venture-bloomberg-2026-09-16/).
[^3]: Carmona, R., Coulon, M., and Schwarz, D. (2013). [Electricity price modeling and asset valuation: a multi-fuel structural approach](https://arxiv.org/abs/1205.2299).
[^4]: MLCommons. [MLPerf Inference: Datacenter](https://mlcommons.org/benchmarks/inference-datacenter/).
[^5]: Amazon Web Services. [Capacity Blocks pricing and billing](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/capacity-blocks-pricing-billing.html).
[^6]: Heath, D., Jarrow, R., and Morton, A. (1992). [Bond Pricing and the Term Structure of Interest Rates: A New Methodology for Contingent Claims Valuation](https://www.jstor.org/stable/2951677). *Econometrica*, 60(1), 77–105.
[^7]: Benth, F. E., Piccirilli, M., and Vargiolu, T. (2018). [Additive energy forward curves in a Heath-Jarrow-Morton framework](https://arxiv.org/abs/1709.03310).
[^8]: Benth, F. E., and Krühner, P. (2014). [Representation of infinite dimensional forward price models in commodity markets](https://arxiv.org/abs/1403.4111).
[^9]: CME Group. [Mark-to-Market](https://www.cmegroup.com/education/courses/introduction-to-futures/mark-to-market.html).
[^10]: Brunnermeier, M. K., and Pedersen, L. H. (2009). [Market Liquidity and Funding Liquidity](https://doi.org/10.1093/rfs/hhn098). *The Review of Financial Studies*, 22(6), 2201–2238.
[^11]: Callegaro, G., Campi, L., Giusto, V., and Vargiolu, T. (2016). [Utility indifference pricing and hedging for structured contracts in energy markets](https://arxiv.org/abs/1407.7725).
