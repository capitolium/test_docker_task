# prepare dependencies
try:
    from flask import Flask     # import flask and docker
    import docker
except ImportError:             # if it fails then run install these modules (they are listed in requirements.txt)
    import pip
    pip.main(['install', '-r', 'requirements.txt'])
    from flask import Flask
    import docker
import json

app = Flask(__name__)

stat = []   # list that contains all statistics

# connect to a docker host, check if it is available and return a docker client object
def gethost():
    try:        
        client = docker.DockerClient(base_url='tcp://127.0.0.1:2375')   # create a docker client
        client.ping()                                                   # check if the client responds
    except:                                                             
        print("trying another host")
        client = docker.from_env()                                      # if it fails create try to create another client from a different address            
    return client

    
@app.route('/date') # tells from which address is this function available
def index():
    global stat
    try:
        client = gethost()                                                      # get a docker client from the function gethost()
        cont = "alpine"                                                         # define container name    
        task = "date"                                                           # define the command to send (e.g. "date" that runs in a linux shell)   
        output = client.containers.run(cont, task, detach=True,remove=True)     # run the container,detach=True returns a container object
                                                                                # remove=True removes the container at the end
        res = output.logs()                                                     # read the output
        stat.append({"container":cont,"result":'success',"msg":''})             # add the result to the statistics
        return res.decode('utf-8')                                              # return the result that will be printed in the console
    except Exception as e:                                                      # if it fails
        stat.append({"container":cont,"result":'failure',"msg":str(e)})         # add to the statistics also the error message    
        return "error"                                                          # print "error" in the console
        
@app.route('/version')
def ver():
    global stat
    try:
        client = gethost()
        cont = "alpine"
        task = "cat /etc/alpine-release "
        output = client.containers.run(cont, task, detach=True,remove=True)
        res = output.logs()
        stat.append({"container":cont,"result":'success',"msg":''}) 
        return res.decode('utf-8')
    except Exception as e:
        stat.append({"container":cont,"result":'failure',"msg":str(e)})
        return "error"
        
@app.route('/hello')
def hello():
    global stat
    try:
        client = gethost()
        cont = "hello-world"
        output = client.containers.run(cont, detach=True,remove=True)
        res = output.logs()
        stat.append({"container":cont,"result":'success',"msg":''}) 
        return res.decode('utf-8')
    except Exception as e:
        stat.append({"container":cont,"result":'failure',"msg":str(e)})
        return "error"
        
# function that calls a non existent container, therefore will always fail       
@app.route('/fail')
def fail():
    global stat
    try:
        client = gethost()
        cont = "dummy"
        output = client.containers.run(cont, detach=True,remove=True)
        res = output.logs()
        stat.append({"container":cont,"result":'success',"msg":''}) 
        return res.decode('utf-8')
    except Exception as e:
        stat.append({"container":cont,"result":'failure',"msg":str(e)}) 
        return "error"

# print the statistics        
@app.route('/stat')
def statistics():
    req = len(stat)     # get the length of the statistics list ( = number of requests sent)
    ok = 0              # initialize variables that store successful and failed requests 
    fail = 0
    newstat = []        # initialize a new temporary list
    for i in stat:                      # loop through the statistics
        if i["result"] == 'success':    # if the request was successful increment the corresponding variable
            ok += 1
        if i["result"] == 'failure':    # do the same for the unsuccessful requests
            fail += 1
    summary = {"total requests":req,"successful":ok,"failed":fail}  # collect the result and add it as first element of the temporary list
    newstat.append(summary)
    newstat.append(stat)                                            # add also the statistics to the temporary list
    out = json.dumps(newstat, indent=4)                             # convert into json
    return out

# print error messages
@app.route('/errors')
def errors():
    errors = []
    for i in stat:                          # collect all the error messages
        if i["result"] == 'failure':
            errors.append(i['msg'])
    out = json.dumps(errors[-3:], indent=2) # get the last 3 error in the list
    return out
   
if __name__ == '__main__':
    #app.run(threaded=True, debug=True) # to enable multithreading and make concurrent requests possible. But in this case is not thread safe because
                                        # two treads may attempt to write into the statistics list and cause a conflict
    app.run(debug=True)
