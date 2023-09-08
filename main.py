import git
import os
import docker
from time import sleep

def delete_olds(tag):
    client = docker.from_env()
    try:
        contenedor = client.containers.get(tag)

        if contenedor.status == 'running':
            contenedor.stop()

        contenedor.remove(force=True) 
        print("El contenedor antiguo se elimino")

    except:
        pass

    try:
        imagen = client.images.get(tag)
        imagen.remove(force=True)
        print("La imagen antigua se elimino")

    except:
        pass

def create_image(tag):
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
        try:
            print(f'Construyendo la imagen Docker {tag}...')

            for build_log in client.api.build(path=repo_dir, tag=tag, decode=True):
                if 'stream' in build_log:
                    print(build_log['stream'], end='')

            print(f'Imagen Docker {tag} creada correctamente')

        except:
            print("Error al crear la imagen")

def create_container(tag, puerto):
    client = docker.from_env()

    try:
        container = client.containers.get(tag)
        print("El contenedor ya existe, prendiendolo...")
        container.start()
        print(f'Contenedor {container.name} en ejecución')

        for log_line in container.logs(stream=True, follow=True):
            print(log_line.decode().strip())

    except:
        print("Creando el contenedor...")
        container = client.containers.run(
            image=tag,
            name=tag,
            detach=True,
            ports={puerto:puerto}
        )

        print(f'Contenedor {container.name} en ejecución')


github_repo_url = 'https://github.com/ValentinCabrera/django-bomberos'
puerto = 8000

repo_dir = "repositorios" + github_repo_url.split('github.com')[1]
tag = repo_dir.replace('/','_').lower()

def update_git():
    if not os.path.exists(repo_dir):
        git.Repo.clone_from(github_repo_url, repo_dir)

    else:
        repo = git.Repo(repo_dir)
        pull = repo.git.pull("origin", "master")

        if pull != "Already up to date.":
            try:
                delete_olds(tag)
                create_image(tag)
                create_container(tag)

            except:
                print("Error")


update_git()
#delete_olds(tag)
#create_image(tag)
create_container(tag, puerto)

while True:
    sleep(30)
    update_git()
