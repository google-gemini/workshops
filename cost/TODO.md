# TODO

## Questions

What are the typical hosting and API costs for different performance tiers of
GenAI models (open vs closed source)?

Proprietary models can be cheaper and also provide things like redundancy,
uptime guarantees.

How do we balance model performance with app responsiveness and overall user
experience? How to reduce latency?

Can reduce latency by using the smallest viable model (with fine-tuning, if
necessary).

What metrics should we use to evaluate the ROI of higher-performing but costlier
models in terms of user engagement and ad revenue?

User engagement (click-through rate, session duration, user retention); ad
revenue; cost per interaction; churn rate.

Are there ways to optimize model performance to reduce costs without sacrificing
quality?

Hybrid stack: cheap models for things like classification; expensive models for
things like final answer response (want that particular bedside manner).

How do licensing costs and terms differ between open and closed source models
for commercial use in mobile apps?

Open source permissive; requires more responsibility for data privacy
regulations and security. Closed source are restrictive (can't train new models
on synthetic data); come with enterprise guarantees for data privacy (no
training on customer data).

What are the main trade-offs in customizability and control between open and
closed source options?

Open source models allow full control over fine-tuning, etc.; require more
expertise and resources to manage. Closed source less flexible, easire to
maintain.

How might using open vs. closed source models affect user trust and privacy
perceptions?

Open source, audits; closed source, mitigated with privacy guarantees.

Cost-benefit tradeoff for finetuning models?

Allows for better alignment with specific tasks / domains (higher engagement);
non-zero cost to fine-tuning; requires high-quality data.

How much data do we need to effectively fine-tune a model?

LLMs can generalize effectively from 10s or 100s of examples; fine-tuned a
Sherlock Holmes on 10,000s of examples, was overkill.

Can fine-tuning help us create more engaging or personalized ad experiences, and
how would we measure this?

Ad engagement metrics (click-through rates, conversion rates). Potentially run
A/B tests.
