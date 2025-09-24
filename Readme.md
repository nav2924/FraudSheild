# 🚀 FraudShield 360  

**AI-Powered UEBA + Tamper-Proof Blockchain Logging, streamed with Kafka, containerized with Docker**  

---

## 📌 TL;DR (30-sec pitch, non-tech)  
Today’s fraud tools are **noisy** (false alarms), **rigid** (rules can’t keep up), and **opaque** (no clear reasons).  

**FraudShield 360** learns each customer’s **normal behaviour**, flags unusual actions, **explains why**, and locks every decision on a **blockchain** so it can’t be secretly changed.  

⚡ Runs in real time with **Kafka** and deploys anywhere with **Docker**.  

---

## ❌ Cons of Existing Systems (Layman’s Terms)  
- 🚫 Too many false alarms → legit customers get blocked.  
- 🐌 Slow to adapt → fraudsters evolve faster than rules.  
- 👓 Tunnel vision → only looks at transactions (ignores devices/logins/peers).  
- ❓ No clear reasons → hard to justify to customers/regulators.  
- 📝 Logs can be edited → weak trust with auditors.  
- 📉 Legacy infra → can’t handle real-time spikes.  

---

## ✅ How FraudShield 360 Solves Them  
- **UEBA baselines** → learns per-user/entity → fewer false alarms.  
- **Anomaly models** → catch new fraud tricks without rules.  
- **Signal fusion** → transactions + logins + device + geo + peers.  
- **Explainability** → human reason codes + SHAP (optional).  
- **Blockchain ledger** → immutable audit (tamper-proof).  
- **Kafka streaming** → elastic, real-time ingestion/scoring.  
- **Docker** → one-click deploy local or cloud.  

---

## 🏗️ Architecture  

### Human Story (non-tech)  
1. We watch **all signals** (money movement, logins, devices, locations).  
2. We know your **normal habits**.  
3. If something looks unusual, the AI raises risk.  
4. We act smartly: allow / OTP selfie / hold / block.  
5. We explain **clearly why**.  
6. We write in **permanent ink** (blockchain).  
7. We learn from feedback every week.  

### Technical Blueprint (engineer view)  
