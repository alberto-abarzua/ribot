// import React from 'react';
import MoveAction from '@/components/actions/MoveAction';
import SleepAction from '@/components/actions/SleepAction';
import ToolAction from '@/components/actions/ToolAction';
import api from '@/utils/api';

const ActionTypes = {
    MOVE: 'move',
    SLEEP: 'sleep',
    TOOL: 'tool',
};

let lastId = 0;
class BaseActionObj {
    constructor(value, type, index, id = -1) {
        if (new.target == BaseActionObj) {
            throw new TypeError('Cannot construct BaseActionObj instances directly');
        }

        this.value = value;
        this.type = type;
        if (id == -1) {
            this.id = BaseActionObj.generateUniqueId();
        } else {
            this.id = id;
        }
        this.index = index;
    }

    static generateUniqueId() {
        const now = Date.now();
        if (now !== lastId) {
            lastId = now;
        } else {
            lastId += 1;
        }
        return lastId;
    }

    render() {
        throw new Error('You have to implement the method render!');
    }

    async run() {
        throw new Error('You have to implement the method run!');
    }

    toSerializable() {
        return {
            value: this.value,
            type: this.type,
            id: this.id,
            index: this.index,
        };
    }

    static fromSerializable(serializable) {
        if (serializable.type == ActionTypes.MOVE) {
            return new MoveActionObj(serializable.value, serializable.index, serializable.id);
        } else if (serializable.type == ActionTypes.SLEEP) {
            return new SleepActionObj(serializable.value, serializable.index, serializable.id);
        } else if (serializable.type == ActionTypes.TOOL) {
            return new ToolActionObj(serializable.value, serializable.index, serializable.id);
        }
    }
}

class MoveActionObj extends BaseActionObj {
    constructor(value, index, id) {
        super(value, ActionTypes.MOVE, index, id);
    }

    render() {
        return (
            <MoveAction
                key={this.id}
                index={this.index}
                id={this.id}
                value={this.value}
            ></MoveAction>
        );
    }
    async run() {
        let pose = {
            x: this.value.x,
            y: this.value.y,
            z: this.value.z,
            roll: this.value.roll,
            pitch: this.value.pitch,
            yaw: this.value.yaw,
        };
        console.log(pose);
        await api.post('/move/pose/move/', pose);
    }
}

class ToolActionObj extends BaseActionObj {
    constructor(value, index, id) {
        super(value, ActionTypes.TOOL, index, id);
    }

    render() {
        return (
            <ToolAction
                key={this.id}
                index={this.index}
                id={this.id}
                value={this.value}
            ></ToolAction>
        );
    }

    async run() {
        let target = {
            toolValue: this.value.toolValue,
        };
        console.log(target);
        await api.post('/move/tool/move/', target);
    }
}

class SleepActionObj extends BaseActionObj {
    constructor(value, index, id) {
        super(value, ActionTypes.SLEEP, index, id);
    }

    render() {
        return (
            <SleepAction
                key={this.id}
                index={this.index}
                id={this.id}
                value={this.value}
            ></SleepAction>
        );
    }
    async run() {
        let duration = this.value.duration;
        console.log('sleeping for ' + duration + ' seconds');
        await this.sleep(duration);
        console.log('resuming after ' + duration + ' seconds');
    }

    sleep(duration) {
        return new Promise(resolve => setTimeout(resolve, duration * 1000));
    }
}

export { MoveActionObj, ToolActionObj, SleepActionObj, ActionTypes, BaseActionObj };
