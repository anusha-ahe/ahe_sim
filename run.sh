docker run -p 5000-5010:5000-5010 -d --name sim sim
docker container exec -it sim bash -c "python3 sim.py"