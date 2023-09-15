import { actionListActions } from '@/redux/ActionListSlice';
import GamesIcon from '@mui/icons-material/Games';

import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import TextVariable from '../general/text/TextVariable';
import BaseAction from './BaseAction';

const MoveAction = ({ ...props }) => {
    const dispatch = useDispatch();

    // get index from props
    const action = useSelector(state => state.actionList.actions[props.index]);

    const [currentPose, setCurrentPose] = useState(action.value);

    useEffect(() => {
        dispatch(
            actionListActions.updateValueByIndex({
                index: props.index,
                value: currentPose,
            })
        );
    }, [currentPose, dispatch, props.index]);

    return (
        <BaseAction
            icon={<GamesIcon className="text-6xl"></GamesIcon>}
            className="bg-slate-400 "
            {...props}
        >
            <>
                <div className="inline-flex flex-1 flex-col items-end justify-center rounded-md bg-slate-200 p-2 text-black shadow">
                    <div className="inline-flex items-center justify-end  ">
                        <TextVariable
                            label="X"
                            value={currentPose.x}
                            setValue={value => setCurrentPose(prev => ({ ...prev, x: value }))}
                            disabled={false}
                        />
                    </div>
                    <div className="inline-flex items-center justify-end">
                        <TextVariable
                            label="Y"
                            value={currentPose.y}
                            setValue={value => setCurrentPose(prev => ({ ...prev, y: value }))}
                            disabled={false}
                        />
                    </div>
                    <div className="inline-flex items-center justify-end">
                        <TextVariable
                            label="Z"
                            value={currentPose.z}
                            setValue={value => setCurrentPose(prev => ({ ...prev, z: value }))}
                            disabled={false}
                        />
                    </div>
                </div>

                <div className="inline-flex  flex-1 flex-col items-end justify-center rounded-md bg-slate-200 p-2 text-black shadow ">
                    <div className="inline-flex items-center justify-end">
                        <TextVariable
                            label="Roll"
                            value={currentPose.roll}
                            setValue={value => setCurrentPose(prev => ({ ...prev, roll: value }))}
                            disabled={false}
                        />
                    </div>
                    <div className="inline-flex items-center justify-end ">
                        <TextVariable
                            label="Pitch"
                            value={currentPose.pitch}
                            setValue={value => setCurrentPose(prev => ({ ...prev, pitch: value }))}
                            disabled={false}
                        />
                    </div>
                    <div className="inline-flex items-center justify-end ">
                        <TextVariable
                            label="Yaw"
                            value={currentPose.yaw}
                            setValue={value => setCurrentPose(prev => ({ ...prev, yaw: value }))}
                            disabled={false}
                        />
                    </div>
                </div>
            </>
        </BaseAction>
    );
};

MoveAction.propTypes = {
    index: PropTypes.number.isRequired,
};

export default MoveAction;
