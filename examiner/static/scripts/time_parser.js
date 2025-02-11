const privates = new WeakMap();

class TimeParser {
    constructor(seconds, init_hours) {
        const secondsPerMinute = 60;
        const secondsPerHour = secondsPerMinute * 60;
        const hoursPerDay = 24;
        
        const time_obj = {
            hours: Math.floor((seconds % (secondsPerHour * hoursPerDay)) / (secondsPerHour)),
            minutes: Math.floor((seconds % (secondsPerHour)) / secondsPerMinute),
            seconds: Math.floor(seconds % secondsPerMinute)
        }
        
        if (!init_hours) {
            delete time_obj.hours;
        }

        privates.set(this, time_obj)
    }

    get hours() {
        return privates.get(this).hours;
    }

    get minutes() {
        return privates.get(this).minutes;
    }

    get seconds() {
        return privates.get(this).seconds;
    }
    
    get units() {
        return Object.values(privates.get(this));
    }

    // units (typically seconds) less than 10, should be prefixed with a zero
    static prefixWithZero(timeUnit) {
        return timeUnit < 10 ? `0${timeUnit}` : timeUnit;
    }
}