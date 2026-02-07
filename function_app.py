import azure.functions as func
from run_once import run

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */20 * * * *", arg_name="timer")
def scheduler(timer: func.TimerRequest):
    run()
