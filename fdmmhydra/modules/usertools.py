def check_user_access(user_groups:list, rules:dict) -> bool:
    if "admins" in user_groups: return True
    for g in user_groups:
        rule = rules.get(g, {})
        if rule in ("one_factor", "two_factor"):
            return True

def check_user_groups(user_groups:list, groups:list) -> bool:
    return "admins" in user_groups or any((u in groups for u in user_groups))

def parse_service_rules(
    rule_list:list,
    default_policy:str = "one_factor",
    default_group:str = "admins"
) -> dict:
    if not len(rule_list):
        return {default_group:default_policy}
    rules = {}
    for rule in rule_list:
        splits = rule.split(":")
        if len(splits) == 1:
            groups, policy = splits, default_policy
        elif len(splits) == 2:
            groups,policy = splits
        else:
            raise ValueError(f"Invalid Access Rule - {rule}")
        rules[groups] = policy
    if not rules.get("admins"): # anti-lockout
        rules = {**{"admins":"one_factor"}, **rules}
    if not rules.get("everybody"):
        rules = {**rules, **{"everybody":"deny"}}
    return rules

def parse_service_settings(services:list) -> dict:
    