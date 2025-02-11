const initHours = Math.floor(_examDuration/60);
const durationSeconds = _examDuration * 60;
// [timerAlertFraction] is a fraction of the total duration such that if the 
// the time remaining is less than, a different style would be applied
// typically red text and scales in and out
const timerAlertFraction = 0.3;

const startTime = getStartTime();
console.log('start time is ', startTime);
const stopTime = startTime + durationSeconds;


let myInterval = setInterval(
    function() {
        // Get today's date and time
        var now = getNow();
        console.log('now is ', now);
        const timeRemaining = stopTime - now;
                    
        const time = new TimeParser(timeRemaining, initHours);
        const timerDom = document.getElementById("timer");
        timerDom.innerHTML = time.units.map(
            unit => TimeParser.prefixWithZero(unit)
        ).join(':');

        if (timeRemaining < (timerAlertFraction * durationSeconds)) {
            timerDom.style.color = 'red';
            timerDom.classList.add('animation-zoom-in-and-out');
        }
        
        if (timeRemaining < 1) {
            timerDom.innerHTML = "Time up";
            endExam();
            clearInterval(myInterval);
        }
    },
    // Update the count down every 1 second
    1000
);