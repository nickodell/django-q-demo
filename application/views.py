from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django_q.tasks import async_task, result, fetch

from . import tasks, models


def get_status(task_id, *args, **kwargs):
    task = fetch(task_id, *args, **kwargs)
    if task is None:
        status = 'in-progress'
    else:
        if task.success:
            status = 'done'
        else:
            status = 'error'
    return status


class SumView(APIView):
    """Get a sum, synchronously."""
    def get(self, request):
        try:
            n = int(request.GET.get('n'))
        except:
            raise APIException("Must provide ?n=<integer> parameter")
        total = 0
        for i in range(1, n + 1):
            total += i

        return Response({'total': total})


class SumAsyncStartView(APIView):
    """Get a sum, asynchronously."""
    def get(self, request):
        try:
            n = int(request.GET.get('n'))
        except:
            raise APIException("Must provide ?n=<integer> parameter")
        
        task = async_task(tasks.get_sum, n)
        progress_url = request.build_absolute_uri(reverse('sum-async-progress') + f"?task_id={task}")

        return Response({'task_progress': progress_url})


class SumAsyncProgressView(APIView):
    """Get the output of a task."""
    def get(self, request):
        task_id = request.GET.get('task_id')
        if task_id is None:
            raise APIException("Must provide ?task_id=<task> parameter")
        task_result = result(task_id, wait=0)
        status = get_status(task_id, wait=0)

        return Response({'status': status, 'total': task_result})


class BuggySumAsyncStartView(APIView):
    """Get a sum, in a way which doesn't work"""
    def get(self, request):
        try:
            n = int(request.GET.get('n'))
        except:
            raise APIException("Must provide ?n=<integer> parameter")
        
        task = async_task(tasks.get_sum_buggy, n)
        progress_url = request.build_absolute_uri(reverse('sum-async-progress') + f"?task_id={task}")

        return Response({'task_progress': progress_url})


class SplitSumAsyncStartView(APIView):
    """Get a sum, using many jobs"""
    def get(self, request):
        try:
            n = int(request.GET.get('n'))
        except:
            raise APIException("Must provide ?n=<integer> parameter")

        # Split problem up into multiple ranges        
        chunks = []
        chunk_size = 100000000  # number of integers per chunk
        for i in range(1, n + 1, chunk_size):
            if i + chunk_size <= n:
                chunks.append((i, i + chunk_size - 1))
            else:
                chunks.append((i, n))

        # Create job in database to attach this data to
        sj = models.SumJob.objects.create()

        # Loop over chunks and send each to task server
        for chunk in chunks:
            n, m = chunk
            async_task(tasks.get_sum_range, sj, n, m)


        # return Response({'total': sum(map(lambda x: tasks.get_sum_range(*x), chunks))})
        return Response({'job_id': sj.id})

class SplitSumAsyncProgressView(APIView):
    """Combine the output of many tasks."""
    def get(self, request):
        try:
            job_id = int(request.GET.get('job_id'))
        except:
            raise APIException("Must provide ?job_id=<job> parameter")

        sj = models.SumJob.objects.get(id=job_id)
        results = models.SumJobComponent.objects \
            .filter(parent_job=sj) \
            .values_list('result', flat=True)

        return Response({'total': sum(results)})
