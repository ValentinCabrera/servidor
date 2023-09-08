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
    tag = get_tag(data)
    repo_dir = get_repo_dir(data)

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

def get_repo_dir(data):
    url = data["url"]
    branch = data["branch"]
    return "repositorios" + url.split('github.com')[1] + "/" + branch

def get_tag(data):
    return get_repo_dir(data).replace('/','_').lower()

def update_repo(data):
    try:
        print("Actualizando repo")
        repo_dir = get_repo_dir(data)
        branch = data["branch"]

        repo = git.Repo(repo_dir)
        return repo.git.pull("origin", branch)
    
    except:
        pass

def is_update(data):
    return update_repo(data) == "Already up to date."
    
def set_up_conteiner(data):
    client = docker.from_env()
    tag = get_tag(data)
    puerto = data["puerto"]

    try:
        container = client.containers.get(tag)
        print("Prendiendo contenedor")
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
    repo_dir = get_repo_dir(data)
    branch = data["branch"]

    if not os.path.exists(repo_dir):
        print("Clonando repo")
        git.Repo.clone_from(data["url"], repo_dir, branch=branch)

def delete_olds(data):
    for func in [delete_old_conteiner, delete_old_image]:
        try:
            func(data)
        except:
            pass

def set_up_server(data):
    print("Setup server")
    for func in [set_up_repo, delete_olds, set_up_image, set_up_conteiner]:
        try:
            func(data)

        except:
            pass

def update_server(data):
    if not is_update(data):
        print("Update server")
        for func in [delete_olds, set_up_image, set_up_conteiner]:
            try:
                func(data)

            except:
                pass

github_repos = [{"url":"https://github.com/juanpid2112/Reservas", "puerto":8000, "branch":"backend"},
                {"url":"https://github.com/juanpid2112/Reservas", "puerto":3000, "branch":"frontend"}]

[set_up_server(repo) for repo in github_repos]

while True:
    [update_server(repo) for repo in github_repos]
    sleep(20)
    
