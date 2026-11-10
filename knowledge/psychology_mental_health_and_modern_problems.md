# Psychology, Mental Health, and Modern Problems — Product Playbook

Extends `reading_habit_psychology.md` (habit mechanics and evidence base).

**Ethical boundary:** this is educational product-design knowledge, not diagnosis or treatment. An app may screen, educate, coach, and escalate — it must not diagnose, prescribe, or replace a licensed professional.

---

## 1. Psychology domains

| Domain | Core question | Product relevance |
|---|---|---|
| Cognitive | Attention, memory, perception, decision-making | Onboarding, focus, information architecture |
| Developmental | Change across lifespan | Age-appropriate UX, parental controls |
| Social | Influence, identity, relationships | Community, accountability, loneliness |
| Personality | Stable traits and differences | Personalization without stereotyping |
| Clinical | Distress, disorder, treatment | Screening, escalation, safety |
| Health | Behavior and illness | Sleep, adherence, chronic care |
| Industrial/organizational | Work, motivation, teams | Burnout, productivity, manager tools |
| Behavioral | Learning, reinforcement, habits | Habit loops, nudges, adherence |

## 2. Stress and coping

- **Lazarus transactional model:** stress = appraisal of demands vs resources; primary appraisal (threat) and secondary appraisal (coping capacity).
- **General Adaptation Syndrome:** alarm → resistance → exhaustion.
- **Allostatic load:** cumulative wear from repeated stress response.
- **Coping styles:** problem-focused, emotion-focused, avoidance; reappraisal, social support, meaning-making.
- **Resilience:** not invulnerability; it is recovery with support, routines, and agency.

**Product rule:** reduce demands (friction, uncertainty, overload) before teaching the user to cope better. Do not put the burden of a badly designed product on the user's resilience.

## 3. Common mental health conditions (overview only)

| Condition | Common experience | When to escalate |
|---|---|---|
| Anxiety disorders | Persistent worry, panic, avoidance | Panic with functional impairment, inability to leave home |
| Depression | Low mood, anhedonia, fatigue, hopelessness | Self-harm thoughts, inability to function, psychosis |
| Bipolar disorder | Mood swings, mania, impulsivity | Mania, risky behavior, no sleep, psychosis |
| PTSD | Intrusion, avoidance, hyperarousal after trauma | Suicidal ideation, severe dissociation |
| OCD | Intrusive thoughts, compulsions | Compulsions consuming hours/day, distress |
| ADHD | Inattention, impulsivity, executive dysfunction | Severe impairment, unsafe behavior |
| Eating disorders | Restriction, bingeing, purging, body image distress | Medical instability, rapid weight loss |
| Substance use | Loss of control, withdrawal, consequences | Withdrawal risk, overdose risk |
| Sleep disorders | Insomnia, apnea, daytime sleepiness | Suspected apnea, severe insomnia |
| Burnout | Exhaustion, cynicism, reduced efficacy | Depression, inability to work |

Use DSM-5-TR / ICD-11 as clinical references, not as app content copied verbatim. Screening tools (PHQ-9, GAD-7) are **screening aids**, not diagnoses; validate licensing and interpretation before use.

## 4. Modern problems worth designing for

| Problem | Signal | App angle |
|---|---|---|
| Loneliness and social isolation | Few close contacts, low belonging | Structured peer groups, accountability, low-pressure connection |
| Digital overload / doomscrolling | Compulsive checking, attention fragmentation | Intention setting, friction, focus sessions, feed limits |
| Burnout | Exhaustion, cynicism, detachment | Workload audit, recovery planning, boundary scripts |
| Sleep deprivation | Short sleep, irregular schedule | Sleep hygiene, wind-down, light/caffeine tracking |
| Financial stress | Debt anxiety, avoidance | Budget clarity, payment plans, shame-free coaching |
| Perfectionism / procrastination | Fear of failure, paralysis | Tiny-step planning, self-compassion, implementation intentions |
| Grief and loss | Persistent sorrow, meaning disruption | Journaling, memorial rituals, support navigation |
| Caregiver burden | Fatigue, resentment, isolation | Respite planning, task sharing, support groups |
| Climate anxiety | Helplessness about the future | Agency-based action plans, community, values clarification |
| Social comparison | Envy, inadequacy from feeds | Private progress, values-based metrics |
| Workplace conflict | Stress, avoidance, escalation | Conversation prep, mediation resources |
| Attention and focus | Context switching, distraction | Environment design, deep-work blocks |

## 5. Human psychology for product design

- **Motivation:** autonomy, competence, relatedness (Self-Determination Theory). Avoid controlling language.
- **Habit loop:** cue → routine → reward; anchor to existing routines; implementation intentions ("if X, then Y").
- **Cognitive load:** chunking, progressive disclosure, recognition over recall.
- **Feedback:** immediate, specific, non-judgmental; show progress, not shame.
- **Trust:** transparency, privacy controls, clear data use, easy deletion.
- **Dark patterns to ban:** fake urgency, guilt trips, hidden cancellation, infinite feeds, streak coercion.
- **Crisis safety:** detect high-risk language, show human resources, avoid automated diagnosis, provide emergency escalation.

## 6. Animal psychology and welfare

Animal behavior is a separate evidence base; never apply human clinical diagnoses to animals.

- **Ethology:** natural behavior, social structure, species-specific needs.
- **Learning theory:** classical conditioning, operant conditioning, reinforcement schedules; punishment is risky and often counterproductive.
- **Welfare:** five freedoms (hunger/thirst, discomfort, pain/injury/disease, fear/distress, expression of normal behavior); enrichment and agency.
- **Common issues:** separation anxiety, fear aggression, resource guarding, compulsive behaviors, house soiling, destructive behavior.
- **Training ethics:** force-free, welfare-first; consult a veterinarian for medical causes and a qualified behaviorist for severe cases.
- **Product angle:** pet routine, enrichment reminders, symptom/behavior diary, vet visit prep, training plans, sitter handoff.

**Red flags:** sudden behavior change, pain, self-injury, appetite loss, aggression with injury risk — refer to a veterinarian or certified behavior professional.

## 7. Assessment and data ethics

1. Do not claim to diagnose.
2. Label screening tools clearly and explain limits.
3. Consent before collecting mood/health data; allow export and deletion.
4. Encrypt sensitive data; minimize retention; do not sell it.
5. Protect vulnerable users, including minors, with age-appropriate safeguards.
6. Human review for high-risk signals; never let an LLM be the sole responder.
7. Use evidence-based content (CBT skills, sleep hygiene, behavioral activation) with citations.
8. Localize crisis resources by country and keep them current.

## 8. Crisis resources (Indonesia-first)

- **Emergency:** 119 (ambulance/emergency).
- **SEJIWA (Kemenkes):** 119 ext. 8 — verify the current number on the official site.
- **Into The Light Indonesia:** https://www.into-the-light.com/
- **International Association for Suicide Prevention:** https://www.iasp.info/
- **Kemenkes:** https://www.kemkes.go.id/

If a user expresses intent to harm self or others, the app should stop normal coaching, show emergency contacts, encourage contacting a trusted person/professional, and avoid leaving the user alone in an automated loop.

## 9. App opportunity matrix

| Idea | User value | Evidence base | Safety burden |
|---|---|---|---|
| Mood and trigger journal | Awareness, pattern detection | CBT, self-monitoring | Medium |
| Guided CBT skills | Skill practice between sessions | CBT, behavioral activation | High |
| Sleep wind-down coach | Better sleep routine | Sleep hygiene, CBT-I principles | Medium |
| Focus and attention trainer | Less fragmentation | Attention research, habit theory | Low |
| Loneliness companion | Structured connection | Social support research | Medium |
| Caregiver planner | Respite and coordination | Caregiver burden research | Medium |
| Pet behavior diary | Better welfare and vet prep | Ethology, learning theory | Medium |
| Burnout recovery plan | Workload and recovery audit | Occupational health | Medium |
| Financial-stress navigator | Reduce avoidance and shame | Behavioral finance, coaching | High (advice boundary) |

## 10. Brainstorming prompts

1. What is the user's actual job-to-be-done, in their words?
2. What is the smallest evidence-based intervention that helps?
3. What does the user do on a bad day, not an ideal day?
4. Where should the app get out of the way?
5. What is the failure mode, and who is harmed?
6. What is the escalation path for high-risk signals?
7. How do we prove benefit without overclaiming?

## 11. Verified resources

WHO: https://www.who.int/news-room/fact-sheets/detail/mental-disorders · https://www.who.int/news-room/fact-sheets/detail/depression
NIMH: https://www.nimh.nih.gov/health/topics
APA: https://www.apa.org/topics · https://www.apa.org/pubs/journals
Psychiatry: https://www.psychiatry.org/patients-families
Research: https://pubmed.ncbi.nlm.nih.gov/ · https://www.semanticscholar.org/ · https://www.frontiersin.org/journals/psychology · https://plos.org/
Crisis: https://www.into-the-light.com/ · https://www.iasp.info/ · https://www.kemkes.go.id/
Animal behavior: https://animalbehavior.org/ · https://www.apa.org/pubs/journals/com · https://www.iaabc.org/
Population data: https://ourworldindata.org/ · https://www.healthdata.org/ · https://www.pewresearch.org/internet/
Some official sites (CDC, Cochrane, Annual Reviews) return 403 to bots but load in a browser.
