# Plant Insight Hub and alerts

> Rules look over the whole plant every 20 seconds: anomalies, causes, impact; fixes are simulated first; daily and weekly reports write themselves.

```anim
name: causal
```

| Where | What |
| --- | --- |
| Plant situation | Each domain's metrics and anomaly counts; you can look back to a past moment |
| Anomalies | Anomaly list, causal chain, handling |
| What-if workbench | Compare several fixes (overtime, another machine, resequencing) in a fast-forwarded copy |
| Action inbox | Drafted actions, executed after approval |
| Daily & weekly reports | Generated automatically |
| Notification settings | Which domains and severities to subscribe to; the in-app bell always receives them, and in production mode email can be sent too |

```goto
tour: ont-anomaly
label: Help me trace an anomaly
```

```goto
tour: ont-inbox
label: Show me the action inbox
```

```ask
q: What is the most serious anomaly right now, and what caused it?
```
