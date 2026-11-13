#!/usr/bin/env python3
"""Offline structural tests; NOT a substitute for Ansible syntax-check or VM deployment."""
from pathlib import Path
import sys
import yaml
from jinja2 import Environment

root = Path(__file__).resolve().parents[1]
files = [
    root / '01_docker_containers.yml',
    root / '02_onlyoffice_workspace.yml',
    root / 'tasks/install_docker.yml',
    root / 'requirements.yml',
    root / 'group_vars/docker_nodes.yml',
    root / 'group_vars/onlyoffice_nodes.yml',
]
for file in files:
    src = file.read_text(encoding='utf-8')
    assert yaml.safe_load(src) is not None, f'Empty YAML: {file}'
    if 'group_vars' not in str(file):
        Environment().parse(src)
    print(f'OK {file.relative_to(root)}')

docker = yaml.safe_load((root / '01_docker_containers.yml').read_text(encoding='utf-8'))[0]
office = yaml.safe_load((root / '02_onlyoffice_workspace.yml').read_text(encoding='utf-8'))[0]
vars_docker = yaml.safe_load((root / 'group_vars/docker_nodes.yml').read_text(encoding='utf-8'))
assert docker['hosts'] == 'docker_nodes'
assert vars_docker['container_count'] == 4
assert vars_docker['default_container_command'] == 'sleep 1d'
assert office['hosts'] == 'onlyoffice_nodes'
commands = [task for task in office['tasks'] if task.get('name', '').startswith('Install ONLYOFFICE once')]
assert commands, 'ONLYOFFICE install block not found'
block = commands[0]['block']
install = next(task for task in block if task['name'].startswith('Install ONLYOFFICE Workspace'))
argv = install['ansible.builtin.command']['argv']
assert argv[argv.index('--installmailserver') + 1] == 'false', 'Mail must be disabled'
assert argv[argv.index('--installationtype') + 1] == 'WORKSPACE', 'Community required'
assert '--communityport' in argv
assert any('community.docker.docker_container' in task for task in docker['tasks'])
assert 'onlyoffice-mail-server' in str(office['tasks'])
print('OK assignment invariants: four containers, Workspace Community, no mail')
print('NOTE: only offline structure checks were executed.')
