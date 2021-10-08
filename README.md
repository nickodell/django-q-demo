# Django Q from Scratch

Django Q is a handy library for creating background tasks using Django. This repo contains code samples to easily get going in using it.

![hero](https://i.kym-cdn.com/photos/images/original/001/059/850/546.gif)



## Software Setup

To complete this tutorial, you'll need the following software:

1. Python
2. [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
3. You'll need to create a virtualenv and install dependencies in it with:

   ```shell
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   ```

## The Problem

Imagine you're developing a data analysis program for DataCo. DataCo has a highly processor-intensive problem they need solved: summing up all of the integers between 1 and N.

```py
total = 0
for i in range(1, n + 1):
	total += i
```

You deploy this code into a Django app, and it works fine - until users start putting larger values into the app. Ten million works fine, a hundred million is a little slow, and three billion takes so long that gunicorn will kill the worker for taking so long:

```
[CRITICAL] WORKER TIMEOUT (pid:32521)
[INFO] Worker exiting (pid: 32521)
```

This time limit is 30 seconds by default. Can you raise this timeout? Yes, a little. But, if you raise it by more than sixty seconds, you run into the timeout of nginx. If you want to raise it by more than *ninety* seconds, you run into the timeout of the user's browser. The further you raise the timeout, the more places you run into new problems.

If you want to do any serious computation, on the scale of minutes, you'll have to do it outside the duration of a single HTTP request. You'll need to trigger a background process, and have that background process provide the result back to Django. This is what Django Q does for you.

## Django Q

Django Q has three different components: the Django server, the task broker, and the task queue server. The Django server is the same as it always is, and responds to HTTP requests from the user. If a request requires background processing, then it can send a task to the broker. The task queue server is responsible for receiving tasks from the broker, processing them, and sending the result back to the broker.

![drawing of Django receiving HTTP requests, task server receiving tasks, and the replies to both](https://i.imgur.com/jCdrHty.png)

But what is a task? It's anything in Python which fulfills three qualities:

1. It is callable. (Example: a function is callable.)
2. The arguments to it are [pickleable](https://stackoverflow.com/questions/3603581/what-does-it-mean-for-an-object-to-be-picklable-or-pickle-able).
3. It doesn't need to be finished before an HTTP response is sent back to the user.

## Getting Started

1. Create a new terminal. Run `docker-compose up`. Leave it running. This runs the task broker.
2. Create a new terminal. Run `./manage.py qcluster`. Leave it running. This runs the task queue server.

   :warning: | Keep in mind that the queue server will *not* reload itself if the code changes, unlike `./manage.py runserver`. You'll have to press Ctrl-C to stop it, then re-run it.
   :---: | :---

3. Open the file `application/views.py` in your text editor or IDE.
4. Create a new terminal. Run `./manage.py runserver`.
5. Go to http://localhost:8000/sum-sync/?n=1000

   This is the synchronous version, which we're going to convert to an asynchronous version.

## Debugging a failing task

I've included a view which starts a broken task. Go to http://localhost:8000/bug-sum-start/?n=100000000

Here are the techniques you can use to debug this problem.

1. Check if the failure still happens in synchronous mode. In the BuggySumAsyncStartView class, change this line:

   ```py
   task = async_task(tasks.get_sum_buggy, n)
   ```

   into this:


   ```py
   task = async_task(tasks.get_sum_buggy, n, sync=True)
   ```

   And refresh the page.

   Instead of sending the task to the queue processor, the task will be executed within Django, and the rest of the view will be paused while the task is running.

   If the error still occurs when running synchronously, then you should debug it that way, because it's always easier than debugging an asynchronous problem.

2. Create a superuser account, and log into the admin console. Click "Failed tasks." Click on the most recent failure. Notice that you can see the traceback and what arguments were provided.

Use the information you've found to fix the bug in tasks.py.

:warning: | Keep in mind that the queue server will *not* reload itself if the code changes, unlike `./manage.py runserver`. You'll have to press Ctrl-C to stop it, then re-run it.
:---: | :---

## Parallelism

One of the ways we can make this faster is to identify pieces of it that we can do in parallel. If we have the sum

>1 + 2 + ... + 9 + 10 + 11 + 12 + ... + 19 + 20

We can break this up into two sums:

>(1 + 2 + ... + 9 + 10) + (11 + 12 + ... + 19 + 20)

Then, those two sums can be evaluated independently. Afterwards, the two sums can be added together to get the result.

In order to parallelize tasks, there are two approaches.

 1. Call `async_task()` multiple times. Since this doesn't wait for the task to finish, you can call it multiple times to do multiple tasks in parallel.
 2. Use the `async_iter()` helper, which creates multiple tasks from an iterable. The first argument is the callable, and the second argument is a list of arguments to provide to each call to the function. The format of the call is similar to the Python builtin map().

The provided code uses `async_iter()`.

### Chunk size

There is a tradeoff in how finely to split a task into multiple pieces: 

 * if you split it into pieces which are too large, then you will not benefit from parallelism.
 * if you split it into pieces which are too small, then the overhead from creating tasks and putting together the results from all of the tasks will be too big.

You should aim for the pieces to take about 5-30 seconds to process. In the provided code, there's a local variable called `chunk_size`. Try using larger or smaller values. How does it change how quickly a result is returned?

## Scaling higher than one node

Django Q can scale to multiple task servers, because the task servers can fetch tasks from the broker over the network. It can also scale to multiple Django servers, because those servers can submit tasks to the broker over the network. This is why Django Q uses a broker: it makes the design more flexible.
