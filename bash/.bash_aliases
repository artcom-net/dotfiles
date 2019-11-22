# Docker
alias dexec='docker exec -it $(docker ps -q) bash'
alias dstop='docker stop $(docker ps -q)'
alias drm='docker rm $(docker ps -aq)'
alias drmi='docker rmi $(docker images -q)'
alias dlog='docker logs -f $(docker ps -q)'

