# Пошаговая памятка: запуск и проверка КТ-2

## Подготовка

1. В Ubuntu на управляющей ВМ установите Ansible: `sudo apt update && sudo apt install -y ansible openssh-client python3`.
2. Установите коллекцию: `ansible-galaxy collection install -r requirements.yml`.
3. Отредактируйте `hosts.ini`: замените примеры `192.168.56.101` и `192.168.56.102` и `ubuntu`.
4. Настройте SSH-ключи и sudo-права; проверьте доступ: `ansible all -m ping`.
5. Выполните статическую проверку: `python3 tests/validate_project.py` и `ansible-playbook --syntax-check 01_docker_containers.yml`.

## Вариант A (4 Docker-контейнера)

```bash
ansible-playbook 01_docker_containers.yml --ask-become-pass
ansible docker_nodes -b -a 'docker ps -a' --ask-become-pass
ansible docker_nodes -b -a 'docker inspect docker1 docker2 docker3 docker4' --ask-become-pass
```

**Успех:** нет `failed`, `unreachable`; присутствуют 4 контейнера с именами `docker1`–`docker4`, образ Ubuntu, команда `sleep 1d`, запущенное состояние `Running=true`. При повторном выполнении не должно возникать ненужного пересоздания контейнеров (хотя скачивание образа может проверить обновления).

## Вариант Б (ONLYOFFICE Workspace Community, Mail отключён)

```bash
ansible-playbook --syntax-check 02_onlyoffice_workspace.yml
ansible-playbook 02_onlyoffice_workspace.yml -e onlyoffice_install_confirm=true --ask-become-pass
ansible onlyoffice_nodes -b -a 'docker ps -a' --ask-become-pass
```

Ожидаются `onlyoffice-community-server`, `onlyoffice-document-server`, `onlyoffice-control-panel`, база данных и вспомогательные контейнеры, но **не** `onlyoffice-mail-server`. После инициализации откройте `http://IP_ВАШЕЙ_ВМ:8080`.

**Требования:** чистая Ubuntu x86_64 ВМ, 4 vCPU, 8 GB RAM, 40+ GiB свободного места. Рекомендуется отдельный хост. Официальный установщик может изменить Docker-сети/каталоги; не запускайте на рабочем сервере без аудита.

## Какие доказательства приложить к сдаче

- Снимок окна с успешным результатом Ansible (PLAY RECAP, failed=0, unreachable=0).
- Снимок `sudo docker ps -a`, показывающий четыре контейнера (вариант A) или компоненты ONLYOFFICE (вариант Б).
- Для ONLYOFFICE: скриншот `docker inspect onlyoffice-mail-server` с сообщением об отсутствии контейнера и страница портала в браузере.
- Ссылка на репозиторий GitHub с исходниками, README и отчётом.

**Обратите внимание:** в этой выдаче нет доказательств реального исполнения на ВМ. Скриншоты и точные результаты должны быть получены только при вашем запуске.
