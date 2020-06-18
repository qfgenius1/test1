###############################################################################
#
#                                 NOTICE:
#  THIS PROGRAM CONSISTS OF TRADE SECRECTS THAT ARE THE PROPERTY OF
#  Advanced Products Ltd. THE CONTENTS MAY NOT BE USED OR DISCLOSED
#  WITHOUT THE EXPRESS WRITTEN PERMISSION OF THE OWNER.
#
#               COPYRIGHT Advanced Products Ltd 2016-2019
#
###############################################################################

from datetime import datetime
from timeit import default_timer as timestamp
import json
from qp_demo_helper import analytic_price
from qp_demo_helper import binomial_price
from qp_demo_helper import finite_differences_price
from qp_demo_helper import get_ql_date
from qp_demo_helper import set_up_option
from qp_demo_helper import read_data_and_get_process
from qp_demo_helper import write_out_data

from qp_api_server import QPAPIServer
from qp_experiment import QPExperiment
from qp_experiment_run import QPExperimentRun

if __name__ == "__main__": 
    bs_price = 0

    ### QP CODE ###
    # set up experiment
    server = QPAPIServer('127.0.0.1', 8080)
    experiment_category = 'demo'
    experiment_name = 'pricer'
    experiment = QPExperiment(server, experiment_category, experiment_name)   
    experiment.get()

    date_time = datetime.now().strftime("%Y/%m/%d:%S")
    ### QP CODE ###
    # start with doing analytic prices
    run_name = 'analytic ' + date_time
    print('running ' + run_name)
    # reading the last message that was sent
    with experiment.new_run(run_name, offset_forwards=False, offset=1) as run:
        # start timer
        start = timestamp()
        
        # read data in from 1 back
        input = run.get_input()
        input_message = input.read()
        input_message_string = input_message.value.decode('utf-8')
        input_data = json.loads(input_message_string)

        # do the pricing
        bsm_process = read_data_and_get_process(input_data)
        bs_price = analytic_price(bsm_process)

        # stop timer
        end = timestamp()
        time_taken = end-start

        # set parameters
        run.set_parameter_value('demo/pricer', 'analytic')
        run.set_parameter_value('demo/steps', 1)
        
        # set metrics
        run.set_metric_value('demo/pricing_error', 0)
        run.set_metric_value('demo/time_taken', time_taken)

        # write the result out
        output_data = write_out_data(run_name, 'analytic', bs_price, time_taken, 1)
        output = run.get_output()
        output.write(str.encode(json.dumps(output_data)))

    ### QP CODE ###
    # binomial pricer
    for step in range(10, 130, 30):
        run_name = 'binomial ' + date_time + ' ' + str(step)
        print('running ' + run_name)
        with experiment.new_run(run_name, offset_forwards=False, offset=1) as run:
            # start timer
            start = timestamp()

            # read data in from 1 back
            input = run.get_input()
            input_message = input.read()
            input_message_string = input_message.value.decode('utf-8')
            input_data = json.loads(input_message_string)

            # do pricing
            bsm_process = read_data_and_get_process(input_data)
            price = binomial_price(bsm_process, step)

            # stop timer
            end = timestamp()
            time_taken = end-start

            # set parameters
            run.set_parameter_value('demo/pricer', 'binomial')
            run.set_parameter_value('demo/steps', step)
        
            # set metrics
            run.set_metric_value('demo/pricing_error', abs(price - bs_price))
            run.set_metric_value('demo/time_taken', time_taken)

            # write the result out
            output_data = write_out_data(run_name, 'binomial', price, time_taken, step)
            output = run.get_output()
            output.write(str.encode(json.dumps(output_data)))

    ### QP CODE ###
    # finite difference pricer
    for step in range(10, 130, 40):
        run_name = 'fd ' + date_time + ' ' + str(step)
        print('running ' + run_name)
        with experiment.new_run(run_name, offset_forwards=False, offset=1) as run:
            # start timer
            start = timestamp()

            # read data in from 1 back
            input = run.get_input()
            input_message = input.read()
            input_message_string = input_message.value.decode('utf-8')
            input_data = json.loads(input_message_string)

            # do pricing
            bsm_process = read_data_and_get_process(input_data)
            fd_price = finite_differences_price(bsm_process, step, step)

            # stop timer
            end = timestamp()
            time_taken = end-start

            # set parameters
            run.set_parameter_value('demo/pricer', 'finite differences')
            run.set_parameter_value('demo/steps', step)
        
            # set metrics
            run.set_metric_value('demo/pricing_error', abs(fd_price - bs_price))
            run.set_metric_value('demo/time_taken', time_taken)

            # write the result out
            output_data = write_out_data(run_name, 'fd', fd_price, time_taken, step)
            output = run.get_output()
            output.write(str.encode(json.dumps(output_data)))

    with experiment.new_run('error ' + date_time) as run:
        # divide by two error
        t = 1/0
    
