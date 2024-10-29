import os
import yaml
from jinja2 import Environment, FileSystemLoader

cwd = os.getcwd()
compose_file_path = os.path.join(cwd, "docker-compose.yml")
authelia_config_path = os.path.join(cwd, "authelia.yml")
readme_template_path = os.path.join(cwd, "README_TEMPLATE.MD")
readme_path = os.path.join(cwd, "README.MD")

class TemplateRenderer():
    def __init__(self, template_dir:os.PathLike, script_template:os.PathLike):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self._render = self.env.get_template(script_template).render

    def render(self, **kw) -> str:
        return self._render(kw)

renderer = TemplateRenderer(cwd, "README_TEMPLATE.MD")
def parse_docker_compose(file_path):
    with open(file_path, 'r') as file:
        compose_data = yaml.safe_load(file)
    services = compose_data.get("services", {})
    containers = []
    for name, service in services.items():
        image = service.get("image", "No image specified")
        labels = service.get("labels", [])
        # Extract description from labels
        description = "No description available"
        for label in labels:
            if label.startswith("homepage.description="):
                description = label.split("=", 1)[1]
                break
        route = ""
        for label in labels:
            if label.startswith("homepage.href="):
                route = "https://"+label.split("=", 1)[1].replace("https://", "").split("/")[0]+"/"
                break
        containers.append({
            "name": name,
            "image": image,
            "description": description,
            "route": route
        })
    # Sort containers alphabetically by name
    containers.sort(key=lambda x: x["name"])
    return containers


def parse_authelia_config(file_path):
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    acl_data = config_data.get("access_control", {})
    default_policy = acl_data.get("default_policy", "deny")
    rules = acl_data.get("rules", [])
    acls = {}
    for r in rules:
        if (domain := r.get("domain", "")):
            prefix = domain.split(".")[0]
        if prefix == '{{ env "DOMAINNAME" }}':
            prefix = '${DOMAINNAME}' # Update based url to docker style
        if not prefix in acls:
            acls[prefix]={"rules":{}}
        policy = r["policy"]
        if not "subject" in r:
            acls[prefix]["rules"]["everybody"]=policy
        else:
            for sub in r["subject"]:
                if sub.startswith("group"):
                    group = sub.split(":")[1]
                else: # per-user etc
                    continue
                acls[prefix]["rules"][group]=policy
    return default_policy, acls


def generate_image_table(containers):
    table = "| Container Name | Image           | Description              |\n"
    table += "| -------------- | --------------- | ------------------------ |\n"
    for container in containers:
        table += f"| {container['name']} | {container['image']} | {container['description']} |\n"
    return table


def generate_routing_table(containers, acls, default_policy):
    table = "| Service Name | Route           | Access Policy   |\n"
    table += "| -------------- | --------------- | --------------- |\n"
    for container in containers:
        if not container['route']:
            continue
        
        prefix = container['route'].split(".")[0].replace("https://", "")
        print(container['route'], prefix, container['name'])
        rules = acls.get(prefix, {}).get("rules", {})
        acl = " ".join([f"**{g}**:*{p}*" for g,p in rules.items() ])
        table += f"| {container['name']} | {container['route']} | { acl } |\n"
    return table


# Parse the file and generate the table
containers = parse_docker_compose(compose_file_path)
default_policy, acls = parse_authelia_config(authelia_config_path)
image_table = generate_image_table(containers)
routing_table = generate_routing_table(containers, acls, default_policy)

output = renderer.render(**{
    "IMAGE_TABLE" : image_table,
    "ROUTING_TABLE" : routing_table,
})


with open(readme_path, "w+") as f:
    f.write(output) 

print(f"{readme_path} regenerated.")