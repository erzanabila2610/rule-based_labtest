import json
import streamlit as st

# -------------------- Load Rules --------------------
rules_json = [
    {
        "name": "Windows open → turn AC off",
        "priority": 100,
        "conditions": [["windows_open", "==", True]],
        "action": {"ac_mode": "OFF", "fan_speed": "LOW", "setpoint": None, "reason": "Windows are open"}
    },
    {
        "name": "No one home → eco mode",
        "priority": 90,
        "conditions": [["occupancy", "==", "EMPTY"], ["temperature", ">=", 24]],
        "action": {"ac_mode": "ECO", "fan_speed": "LOW", "setpoint": 27, "reason": "Home empty; save energy"}
    },
    {
        "name": "Hot & humid (occupied) → cool strong",
        "priority": 80,
        "conditions": [["occupancy", "==", "OCCUPIED"], ["temperature", ">=", 30], ["humidity", ">=", 70]],
        "action": {"ac_mode": "COOL", "fan_speed": "HIGH", "setpoint": 23, "reason": "Hot and humid"}
    },
    {
        "name": "Hot (occupied) → cool",
        "priority": 70,
        "conditions": [["occupancy", "==", "OCCUPIED"], ["temperature", ">=", 28]],
        "action": {"ac_mode": "COOL", "fan_speed": "MEDIUM", "setpoint": 24, "reason": "Temperature high"}
    },
    {
        "name": "Slightly warm (occupied) → gentle cool",
        "priority": 60,
        "conditions": [["occupancy", "==", "OCCUPIED"], ["temperature", ">=", 26], ["temperature", "<", 28]],
        "action": {"ac_mode": "COOL", "fan_speed": "LOW", "setpoint": 25, "reason": "Slightly warm"}
    },
    {
        "name": "Night (occupied) → sleep mode",
        "priority": 75,
        "conditions": [["occupancy", "==", "OCCUPIED"], ["time_of_day", "==", "NIGHT"], ["temperature", ">=", 26]],
        "action": {"ac_mode": "SLEEP", "fan_speed": "LOW", "setpoint": 26, "reason": "Night comfort"}
    },
    {
        "name": "Too cold → turn off",
        "priority": 85,
        "conditions": [["temperature", "<=", 22]],
        "action": {"ac_mode": "OFF", "fan_speed": "LOW", "setpoint": None, "reason": "Already cold"}
    }
]

# -------------------- Evaluate Rule --------------------
def check_condition(value, op, target):
    if op == "==":
        return value == target
    elif op == ">=":
        return value >= target
    elif op == "<=":
        return value <= target
    elif op == "<":
        return value < target
    elif op == ">":
        return value > target
    else:
        return False

def decide_ac_action(facts, rules):
    # Sort rules by priority descending
    sorted_rules = sorted(rules, key=lambda r: r["priority"], reverse=True)
    for rule in sorted_rules:
        if all(check_condition(facts.get(cond[0]), cond[1], cond[2]) for cond in rule["conditions"]):
            return rule["action"], rule["name"]
    # Default if no rule matched
    return {"ac_mode": "OFF", "fan_speed": "LOW", "setpoint": None, "reason": "No matching rule"}, "No rule"

# -------------------- Streamlit UI --------------------
st.title("Smart Home AC Controller")

st.subheader("Input Home Conditions")
temperature = st.number_input("Temperature (°C)", value=22)
humidity = st.number_input("Humidity (%)", value=46)
occupancy = st.selectbox("Occupancy", ["OCCUPIED", "EMPTY"], index=0)
time_of_day = st.selectbox("Time of Day", ["MORNING", "AFTERNOON", "EVENING", "NIGHT"], index=3)
windows_open = st.checkbox("Windows Open", value=False)

if st.button("Decide AC Action"):
    home_facts = {
        "temperature": temperature,
        "humidity": humidity,
        "occupancy": occupancy,
        "time_of_day": time_of_day,
        "windows_open": windows_open
    }
    
    action, rule_name = decide_ac_action(home_facts, rules_json)
    
    st.subheader("AC Decision")
    st.write(f"**Rule applied:** {rule_name}")
    st.write(f"**AC Mode:** {action['ac_mode']}")
    st.write(f"**Fan Speed:** {action['fan_speed']}")
    st.write(f"**Setpoint:** {action['setpoint']}")
    st.write(f"**Reason:** {action['reason']}")
