import BaseAction from './BaseAction';
import TextVariable from '../general/text/TextVariable';
import { actionListActions } from '@/redux/ActionListSlice';
import api from '@/utils/api';
import GamesIcon from '@mui/icons-material/Games';
import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';

const MoveAction = ({ action, ...props }) => {
    const id = action.id;

    const dispatch = useDispatch();

    const [currentPose, setCurrentPose] = useState(action.value);

    useEffect(() => {
        const checkValid = async () => {
            let pose = {
                x: currentPose.x,
                y: currentPose.y,
                z: currentPose.z,
                roll: currentPose.roll,
                pitch: currentPose.pitch,
                yaw: currentPose.yaw,
            };
            try {
                const res = await api.post('/move/pose/validate/', pose);
                if (res.status === 200) {
                    dispatch(actionListActions.setValidStatus({ actionId: id, valid: true }));
                }
            } catch (err) {
                dispatch(actionListActions.setValidStatus({ actionId: id, valid: false }));
            }
        };

        checkValid();
    }, [currentPose, dispatch, id]);

    useEffect(() => {
        dispatch(actionListActions.setActionValue({ actionId: id, value: currentPose }));
    }, [currentPose, dispatch, id]);
    return (
        <BaseAction
            icon={<GamesIcon className="text-6xl"></GamesIcon>}
            action={action}
            className=" bg-action-move"
            {...props}
        >
            <div className="flex flex-1 items-center justify-end gap-x-4">
                <div className="inline-flex flex-col items-end justify-center rounded-md bg-action-data p-2 text-black shadow">
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

                <div className="inline-flex flex-col items-end justify-center rounded-md bg-action-data p-2 text-black shadow ">
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
            </div>
        </BaseAction>
    );
};

MoveAction.propTypes = {
    action: PropTypes.shape({
        id: PropTypes.number.isRequired,
        parentId: PropTypes.number,
        running: PropTypes.bool.isRequired,
        valid: PropTypes.bool.isRequired,
        value: PropTypes.shape({
            x: PropTypes.number.isRequired,
            y: PropTypes.number.isRequired,
            z: PropTypes.number.isRequired,
            roll: PropTypes.number.isRequired,
            pitch: PropTypes.number.isRequired,
            yaw: PropTypes.number.isRequired,
        }).isRequired,
    }).isRequired,
};

export default MoveAction;
