# DevSecOps - Контрольная работа № 2 (KT-2)

**Студент:** Алакберова Симран Ахлиман  
**Группа:** 4П1.23


Готовый учебный проект **Ansible + Docker** по двум выданным материалам.

**Выбор для сдачи:**

- **Вариант A (`01_docker_containers.yml`)** - основное задание по 10-страничному методическому материалу: установка Docker из официального APT-репозитория и создание **4 контейнеров** `docker1`-`docker4` на образе Ubuntu с командой `sleep 1d`.
- **Вариант Б (`02_onlyoffice_workspace.yml`)** - альтернатива из короткого файла «KT-2»: установка **ONLYOFFICE Workspace Community** с использованием Docker и официального установочного скрипта, **БЕЗ почтового сервера** (`--installmailserver false`).

Оба варианта подготовлены: можно разместить их в одном репозитории GitHub, но запускать на **разных лабораторных ВМ**. **На реальной машине выполнение не подтверждалось.**

## Состав проекта

```text
DevSecOps_KT2_Ansible/
├── 01_docker_containers.yml       # вариант A: 4 контейнера
├── 02_onlyoffice_workspace.yml    # вариант Б: ONLYOFFICE без почты
├── tasks/install_docker.yml       # общие задачи установки Docker
├── hosts.ini                      # пример Inventory; измените адреса
├── ansible.cfg
├── requirements.yml              # коллекция community.docker
├── group_vars/
│   ├── docker_nodes.yml
│   └── onlyoffice_nodes.yml
├── tests/validate_project.py      # локальная структурная проверка
├── docs/COMMANDS.md               # все команды и критерии проверки
├── .gitignore
└── report/KT2_DevSecOps_Report.docx
```

## 1. Подготовка управляющей ВМ (Ubuntu)

```bash
sudo apt update
sudo apt install -y ansible openssh-client python3
ansible-galaxy collection install -r requirements.yml
ansible --version
```

На каждой целевой Ubuntu ВМ нужна учётная запись с `sudo`, работающим SSH и доступом к сети. Настройка SSH-ключа на управляющей ВМ:

```bash
ssh-keygen -t ed25519
ssh-copy-id ubuntu@192.168.56.101
ssh-copy-id ubuntu@192.168.56.102
```

Измените значения IP и пользователя в **`hosts.ini`** на адреса вашей лаборатории. Не сохраняйте приватные ключи и реальные пароли в публичном репозитории. Для ограничения доступа проверьте SSH-host keys перед первым подключением.

Проверка соединения с отдельными группами:

```bash
ansible docker_nodes -m ansible.builtin.ping
ansible onlyoffice_nodes -m ansible.builtin.ping
```

Если у `sudo` есть пароль, добавьте `--ask-become-pass` к запуску плейбуков. Настройка ключей не означает автоматического доступа к серверам.

## 2. Вариант A - Docker и четыре контейнера

```bash
ansible-playbook --syntax-check 01_docker_containers.yml
ansible-playbook 01_docker_containers.yml --ask-become-pass
```

Конфигурация в `group_vars/docker_nodes.yml`: 4 контейнера `docker1`, `docker2`, `docker3`, `docker4`, образ `ubuntu:24.04`, команда `sleep 1d`. Контейнеры запускаются через `community.docker.docker_container`, ограничиваются 128 МБ ОЗУ, лишаются сетевых интерфейсов и дополнительных capabilities. Это безопаснее обычной лабораторной демонстрации, не мешая `sleep`.

Проверка на целевой ВМ:

```bash
ssh ubuntu@192.168.56.101
sudo docker --version
sudo docker ps -a --filter name=docker
sudo docker inspect docker1 docker2 docker3 docker4
sudo docker exec docker1 cat /etc/os-release
```

Все 4 контейнера должны присутствовать; после запуска в `docker ps` они имеют статус `Up`. Поскольку `sleep 1d` заканчивается через сутки, `restart_policy: unless-stopped` запускает контейнер заново, пока его не остановят вручную.

## 3. Вариант Б - ONLYOFFICE Workspace без почты

**Системные требования по инструкции ONLYOFFICE:** выделенная Ubuntu AMD64 ВМ, не меньше 4 vCPU, около 8 ГБ RAM, 40 ГБ свободного места; установщик обычно создаёт swap. Требуется интернет для скачивания образов. В проекте выбран порт **8080**, чтобы избежать конфликта с уже работающим Nginx на порту 80.

**Осторожно:** скрипт устанавливает несколько тяжёлых сервисов на сервер и скачивает дополнительные образы. `onlyoffice_install_confirm` по умолчанию `false`; явно подтвердите установку только на предназначенной для этого тестовой ВМ.

```bash
ansible-playbook --syntax-check 02_onlyoffice_workspace.yml
ansible-playbook 02_onlyoffice_workspace.yml \
  -e onlyoffice_install_confirm=true --ask-become-pass
```

Используется *официальный Docker-установщик* (`install.sh`) вместо интерактивной обёртки `workspace-install.sh`, чтобы Ansible мог выполнить установку без меню. Команды переключают тип установки на `WORKSPACE` (Community) и передают `--installmailserver false`: этот параметр соответствует официальному `-ims false`. Пароли MySQL генерируются **на сервере**, хранятся в директории root с правами `0700`, в GitHub не попадают; задача запуска имеет `no_log: true`.

Для более строгой защиты цепочки поставки перед запуском проверьте содержимое скачанного скрипта и задайте `onlyoffice_installer_sha256` в `group_vars/onlyoffice_nodes.yml` (64 hex-символа). Без него `get_url` проверяет TLS, но **не фиксирует содержимое файла по хешу**. В продакшене рекомендуется дополнительно ограничить доступ по HTTPS и пересмотреть настройки портов/секретов.

Проверка на целевой ВМ:

```bash
ssh ubuntu@192.168.56.102
sudo docker ps -a
sudo docker inspect onlyoffice-community-server onlyoffice-document-server onlyoffice-control-panel
! sudo docker inspect onlyoffice-mail-server >/dev/null 2>&1 && echo 'Mail Server отсутствует'
```

Откройте в браузере: **`http://192.168.56.102:8080`** (замените IP адресом своей ВМ). При первом запуске сервисам требуется время для инициализации.

## 4. Проверки перед сдачей и публикация на GitHub

```bash
python3 tests/validate_project.py
ansible-playbook --syntax-check 01_docker_containers.yml
ansible-playbook --syntax-check 02_onlyoffice_workspace.yml
```

Далее получите реальные результаты `docker ps -a` на вашей ВМ и сделайте скриншоты; не подменяйте их образцовыми выводами. **Структурная проверка YAML/Jinja2 не равна полноценному `ansible-playbook --syntax-check` или запуску на сервере.**

Для загрузки на GitHub откройте репозиторий → **Add file → Upload files**, загрузите **содержимое распакованной папки проекта**, сохраните `README.md` в корне, нажмите **Commit changes**. Удостоверьтесь, что ни один секрет, приватный ключ или `*.secret` не был загружен.

## Ссылки

- Методические материалы KT-2 (оба документа преподавателя).
- [Docker Engine / Ubuntu - official docs](https://docs.docker.com/engine/install/ubuntu/)
- [ONLYOFFICE Workspace Community / script installation](https://helpcenter.onlyoffice.com/workspace/installation/community/docker/installing/workspace-install)
- [ONLYOFFICE Workspace / script parameters](https://helpcenter.onlyoffice.com/workspace/installation/community/docker/installing/workspace-install-parameters)
- [Official ONLYOFFICE installation scripts](https://github.com/ONLYOFFICE/OneClickInstall-Workspace)
- [Ansible community.docker collection](https://docs.ansible.com/ansible/latest/collections/community/docker/index.html)
