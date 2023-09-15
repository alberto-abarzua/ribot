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

    run() {
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
    run() {
        api.post;
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

    run() {}
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
    run() {}
}

export { MoveActionObj, ToolActionObj, SleepActionObj, ActionTypes, BaseActionObj };
