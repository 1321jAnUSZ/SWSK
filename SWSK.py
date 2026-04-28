import socket

ipadress = "127.0.0.1"
port = 7424

states = {}

buffer = ""

interested = {"Bł_B606", "Bł_606", "Bł_605"}

rules = [
    {
        "name": "Przebieg_1",
        "trigger": ("Bł_B606", "S10a"),
        "condtions": {
            "Bł_606": "+",
            "Bł_605": "+"
        },
        "action": ("Bł_B606", "W19")
    }
]


def condtions_met(rule,states):
    for key, expected in rule["condtions"].items():
        if states.get(key) != expected:
            return False
        
    return True

def processRules(name, value, sock):
    for rule in rules:
        trigger_name, trigger_value = rule["trigger"]

        if name != trigger_name or value != trigger_value:
            continue

        if not condtions_met(rule, states):
            continue
        
        action_name, action_value = rule["action"]
        print(action_name, action_value)
        msg = f"{action_name}:{action_value}\r\n"
        print(repr(msg))
        sock.sendall(msg.encode("utf-8"))
        print("Wysłano polecenie")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ipadress,port))
    s.sendall(b"GetState\r\n")

    while True:
        data = s.recv(2048)
        if not data:
            break

        buffer +=data.decode(errors="ignore")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if ":" not in line:
                continue

            name, value = line.split(":", 1)
            name = name.strip().replace("\x00", "")
            value = value.strip()

            if name not in interested:
                continue

            prev = states.get(name)
            if prev == value:
                continue

            states[name] = value
            print(f"{name} -> {value}")
            processRules(name, value, s)
