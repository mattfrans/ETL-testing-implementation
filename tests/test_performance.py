import pytest
import time
import psutil
import os
import gc
import threading
import tracemalloc
import concurrent.futures
from functools import wraps
import cProfile
import pstats
import pandas as pd
from pipeline.etl import SimpleExtractor, SimpleTransformer, SimpleLoader, run_etl
from pipeline.models import VantaaOpenApplications, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

"""
Performance tests have been commented out as they are not necessary for this ETL pipeline.
Reasons:
1. Small data volume (< 100 records)
2. Simple operations (basic transformations)
3. No real-time requirements
4. Single-user, file-based SQLite database

See TESTING_DOCUMENTATION.md for detailed analysis of why performance testing isn't needed
and what types of testing would be more valuable for this pipeline.
"""

# def get_process_memory():
#     """Get current process memory usage in MB"""
#     process = psutil.Process(os.getpid())
#     return process.memory_info().rss / 1024 / 1024

# class ResourceMonitor:
#     """Monitor system resources during test execution"""
#     def __init__(self):
#         self.cpu_percent = []
#         self.memory_percent = []
#         self._stop = False
        
#     def start_monitoring(self):
#         while not self._stop:
#             self.cpu_percent.append(psutil.cpu_percent())
#             self.memory_percent.append(psutil.virtual_memory().percent)
#             time.sleep(0.1)
            
#     def stop_monitoring(self):
#         self._stop = True

# def profile_performance(func):
#     """Decorator to profile performance of test functions"""
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         profiler = cProfile.Profile()
#         result = profiler.runcall(func, *args, **kwargs)
#         stats = pstats.Stats(profiler)
#         stats.sort_stats('cumulative')
#         stats.print_stats(20)  # Print top 20 time-consuming operations
#         return result
#     return wrapper

# def setup_test_db():
#     """Helper function to set up a test database"""
#     engine = create_engine('sqlite:///:memory:')
#     Base.metadata.create_all(engine)
#     return engine

class TestPerformance:
    """
    Performance tests are commented out as they are not necessary for this ETL pipeline.
    See docstring at top of file and TESTING_DOCUMENTATION.md for detailed explanation.
    """
    pass

#     @pytest.fixture(autouse=True)
#     def setup_database(self):
#         """Setup a test database"""
#         self.engine = setup_test_db()
#         Session = sessionmaker(bind=self.engine)
#         self.session = Session()
#         yield self.session
#         self.session.close()

#     def test_extraction_performance(self, benchmark):
#         """Benchmark the data extraction performance"""
#         extractor = SimpleExtractor()
#         result = benchmark(extractor.extract)
#         assert result is not None
#         assert benchmark.stats.stats.mean < 2.0, f"Extraction performance below threshold: {benchmark.stats.stats.mean:.2f}s"

#     @pytest.mark.parametrize("data_size", [100, 1000, 10000])
#     def test_transformation_scalability(self, data_size):
#         """Test performance scaling with different data sizes"""
#         test_data = {
#             "id": range(data_size),
#             "ammattiala": [f"Field {i}" for i in range(data_size)],
#             "tyotehtava": [f"Job {i}" for i in range(data_size)],
#             "tyoavain": [f"Key {i}" for i in range(data_size)],
#             "osoite": [f"Address {i}" for i in range(data_size)],
#             "haku_paattyy_pvm": ["2024-12-31"] * data_size,
#             "x": [25.0] * data_size,
#             "y": [60.0] * data_size,
#             "linkki": [f"http://example.com/{i}" for i in range(data_size)]
#         }
#         df = pd.DataFrame(test_data)
        
#         transformer = SimpleTransformer()
#         start_time = time.time()
#         transformed_df = transformer.transform(df)
#         end_time = time.time()
        
#         execution_time = end_time - start_time
#         assert execution_time < (data_size * 0.001), f"Performance doesn't scale linearly: {execution_time:.2f}s for {data_size} records"

#     @profile_performance
#     def test_profiled_pipeline(self):
#         """Profile the performance of the entire ETL pipeline"""
#         run_etl(str(self.engine.url))

#     def test_memory_leaks(self):
#         """Test for memory leaks during ETL process"""
#         tracemalloc.start()
#         initial_memory = get_process_memory()
        
#         # Run ETL multiple times
#         for _ in range(5):
#             run_etl(str(self.engine.url))
#             gc.collect()
        
#         final_memory = get_process_memory()
#         tracemalloc.stop()
        
#         memory_increase = final_memory - initial_memory
#         assert memory_increase < 50, f"Memory leak detected: {memory_increase:.2f}MB increase"

#     def test_concurrent_performance(self):
#         """Test performance under concurrent load"""
#         def run_concurrent_etl():
#             engine = setup_test_db()
#             return run_etl(str(engine.url))

#         with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
#             start_time = time.time()
#             futures = [executor.submit(run_concurrent_etl) for _ in range(4)]
#             concurrent.futures.wait(futures)
#             end_time = time.time()

#         total_time = end_time - start_time
#         assert total_time < 8.0, f"Concurrent performance below threshold: {total_time:.2f}s"

#     def test_resource_usage(self):
#         """Test CPU and memory usage during ETL process"""
#         monitor = ResourceMonitor()
#         monitor_thread = threading.Thread(target=monitor.start_monitoring)
#         monitor_thread.start()
        
#         run_etl(str(self.engine.url))
        
#         monitor.stop_monitoring()
#         monitor_thread.join()
        
#         avg_cpu = sum(monitor.cpu_percent) / len(monitor.cpu_percent)
#         avg_memory = sum(monitor.memory_percent) / len(monitor.memory_percent)
        
#         assert avg_cpu < 80.0, f"High CPU usage detected: {avg_cpu:.2f}%"
#         assert avg_memory < 80.0, f"High memory usage detected: {avg_memory:.2f}%"

#     def test_batch_processing_performance(self):
#         """Test performance of batch data processing"""
#         batch_sizes = [100, 500, 1000]
#         processing_times = []
        
#         for size in batch_sizes:
#             test_data = pd.DataFrame({
#                 "id": range(size),
#                 "ammattiala": [f"Field {i}" for i in range(size)],
#                 "tyotehtava": [f"Job {i}" for i in range(size)],
#                 "tyoavain": [f"Key {i}" for i in range(size)],
#                 "osoite": [f"Address {i}" for i in range(size)],
#                 "haku_paattyy_pvm": ["2024-12-31"] * size,
#                 "x": [25.0] * size,
#                 "y": [60.0] * size,
#                 "linkki": [f"http://example.com/{i}" for i in range(size)]
#             })
            
#             transformer = SimpleTransformer()
#             start_time = time.time()
#             transformed_df = transformer.transform(test_data)
#             end_time = time.time()
            
#             processing_times.append(end_time - start_time)
        
#         # Check if processing time scales roughly linearly
#         time_ratios = [t2/t1 for t1, t2 in zip(processing_times[:-1], processing_times[1:])]
#         for ratio in time_ratios:
#             assert 1.0 <= ratio <= 6.0, f"Non-linear batch processing performance detected: ratio {ratio:.2f}"

# class TestPerformanceRegression:
#     """Track performance metrics over time to detect regressions"""
    
#     def __init__(self):
#         self.benchmark_file = "performance_benchmarks.txt"

#     def store_benchmark_results(self, result):
#         """Store benchmark results for future comparison"""
#         with open(self.benchmark_file, "a") as f:
#             f.write(f"{time.time()},{result.stats.mean}\n")

#     def get_historical_mean(self):
#         """Get historical mean performance"""
#         if not os.path.exists(self.benchmark_file):
#             return float('inf')
        
#         times = []
#         with open(self.benchmark_file, "r") as f:
#             for line in f:
#                 _, mean = line.strip().split(",")
#                 times.append(float(mean))
#         return sum(times) / len(times)

#     def test_performance_regression(self, benchmark):
#         """Track performance metrics over time"""
#         extractor = SimpleExtractor()
#         result = benchmark(extractor.extract)
        
#         self.store_benchmark_results(result)
#         historical_mean = self.get_historical_mean()
        
#         assert result.stats.mean <= historical_mean * 1.1, \
#             f"Performance regression detected: current {result.stats.mean:.2f}s vs historical {historical_mean:.2f}s"
