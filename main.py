import git
import os
import docker
from time import sleep

def delete_old_conteiner(data):
    print("Eliminando contenedor")
    client = docker.from_env()
    tag = get_tag(data)

    try:
        contenedor = client.containers.get(tag)

        if contenedor.status == 'running':
            contenedor.stop()

        contenedor.remove(force=True) 

    except:
        pass

def delete_old_image(data):
    print("Eliminando imagen")
    client = docker.from_env()
    tag = get_tag(data)

    try:
        imagen = client.images.get(tag)
        imagen.remove(force=True)

    except:
        pass

def set_up_image(data):
    tag = get_tag(data["url"])
    repo_dir = get_repo_dir(data["url"])

    def verify_existence():
        images_tags = []

        for i in client.images.list():
            try:
                images_tags.append(i.attrs["RepoTags"][0].split(":")[0])
            
            except:
                pass

        return tag in images_tags

    client = docker.from_env()

    if not verify_existence():
        print("Creando imagen")
        for build_log in client.api.build(path=repo_dir, tag=tag, decode=True):
            if 'stream' in build_log:
                print(build_log['stream'], end='')

def get_repo_dir(url):
    return "repositorios" + url.split('github.com')[1]

def get_tag(url):
    return get_repo_dir(url).replace('/','_').lower()

def update_repo(data):
    print("Actualizando repo")
    repo_dir = get_repo_dir(data["url"])
    branch = data["branch"]

    repo = git.Repo(repo_dir)
    return repo.git.pull("origin", branch)

def is_update(data):
    return update_repo(data) == "Already up to date."
    
def set_up_conteiner(data):
    client = docker.from_env()
    tag = get_tag(data["url"])
    puerto = data["puerto"]

    try:
        print("Prendiendo contenedor")
        container = client.containers.get(tag)
        container.start()

    except:
        print("Creando contenedor")
        container = client.containers.run(
            image=tag,
            name=tag,
            detach=True,
            ports={puerto:puerto}
        )

    print(f'Contenedor {container.name} en ejecución')

def set_up_repo(data):
    print("Setup repo")
    repo_dir = get_repo_dir(data["url"])

    if not os.path.exists(repo_dir):
        print("Clonando repo")
        git.Repo.clone_from(data["url"], repo_dir)

    else:
        if not is_update(data):
            delete_old_conteiner(data)
            delete_old_image(data)

def set_up_server(data):
    print("Setup server")
    set_up_repo(data)
    set_up_image(data)
    set_up_conteiner(data)

def update_server(data):
    if not is_update(data):
        print("Update server")
        delete_old_conteiner(data)
        delete_old_image(data)
        set_up_image(data)
        set_up_conteiner(data)

github_repos = [{"url":"https://github.com/ValentinCabrera/django-bomberos", "puerto":8000, "branch":"master"}]
[set_up_server(repo) for repo in github_repos]

while True:
    [update_server(repo) for repo in github_repos]
    sleep(20)
    
