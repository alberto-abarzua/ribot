import {
    ContextMenu,
    ContextMenuContent,
    ContextMenuItem,
    ContextMenuLabel,
    ContextMenuTrigger,
} from '@/components/ui/context-menu';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { actionListActions } from '@/redux/ActionListSlice';
import { getActionForDownload, runAction } from '@/utils/actions';
import { PositionTypes, dragLocation } from '@/utils/dragndrop';
import { ItemTypes } from '@/utils/ItemTypes';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import CloseIcon from '@mui/icons-material/Close';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DownloadIcon from '@mui/icons-material/Download';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import ErrorIcon from '@mui/icons-material/Error';
import MenuOpenIcon from '@mui/icons-material/MenuOpen';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PropTypes from 'prop-types';
import { useRef } from 'react';
import { useEffect, useState } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { useDispatch } from 'react-redux';

const BaseAction = ({ icon, children, className, action, ...props }) => {
    const id = action.id;
    const dispatch = useDispatch();
    const [url, setUrl] = useState(null);

    useEffect(() => {
        let actionForDownload = getActionForDownload(action);
        actionForDownload = JSON.stringify(actionForDownload);
        const blob = new Blob([actionForDownload], { type: 'application/json' });

        setUrl(window.URL.createObjectURL(blob));
    }, [action]);

    const running = action.running;
    const valid = action.valid;

    const ref = useRef(null);

    const [{ handlerId }, drop] = useDrop({
        accept: [ItemTypes.ACTION],
        collect(monitor) {
            return {
                handlerId: monitor.getHandlerId(),
            };
        },
        hover(item, monitor) {
            const dragPos = dragLocation(ref, monitor);

            if (
                id == item.id ||
                item.id == action.parentId ||
                dragPos === PositionTypes.OUT ||
                dragPos === PositionTypes.MIDDLE
            )
                return;

            dispatch(
                actionListActions.moveAction({
                    refActionId: item.id,
                    targetActionId: id,
                    before: dragPos === PositionTypes.TOP,
                    type: item.type,
                    value: item.value,
                })
            );
        },
    });

    const [{ isDragging }, drag, dragPreview] = useDrag({
        type: ItemTypes.ACTION,
        item: { id },
        collect: monitor => ({
            isDragging: monitor.isDragging(),
        }),
        isDragging: monitor => id === monitor.getItem().id,
    });

    dragPreview(drop(ref));

    const onDelete = () => {
        dispatch(actionListActions.deleteAction({ actionId: id }));
    };

    const onDuplicate = () => {
        dispatch(actionListActions.duplicateAction({ actionId: id }));
    };

    const onRun = async () => {
        dispatch(actionListActions.setRunningStatus({ actionId: id, running: true }));
        await runAction(action, dispatch);
        dispatch(actionListActions.setRunningStatus({ actionId: id, running: false }));
    };

    const menuItems = [
        { label: 'Duplicate', icon: <ContentCopyIcon />, onClick: onDuplicate },
        {
            label: (
                <a href={url} download={`${action.type}.json`}>
                    Download
                </a>
            ),
            icon: <DownloadIcon />,
            onClick: () => {},
        },
        { label: 'Run', icon: <PlayArrowIcon />, onClick: onRun },
    ];

    let indicator = valid ? (
        running ? (
            <AutorenewIcon className="animate-spin text-4xl transition-all duration-300 group-hover:text-gray-600" />
        ) : (
            <div className="p-3" onMouseDown={e => e.stopPropagation()} ref={drag}>
                <DragIndicatorIcon className="mx-3 scale-150 transform transition-all duration-300 hover:text-slate-300" />
            </div>
        )
    ) : (
        <ErrorIcon className="scale-150 transform text-red-500 transition-all duration-300 group-hover:text-gray-600" />
    );

    if (!isDragging) {
        return (
            <ContextMenu>
                <ContextMenuTrigger>
                    <div
                        className={`transform transition-all ${
                            valid ? '' : 'bg-red-900'
                        } duration-100 ${className} group relative flex w-full shrink-0 items-center justify-center space-x-4 overflow-hidden rounded-md px-6 py-3 text-white shadow`}
                        {...props}
                        ref={ref}
                        data-handler-id={handlerId}
                    >
                        <div className="flex flex-shrink-0 items-center justify-start">{icon}</div>
                        {children}
                        <div className="flex cursor-grab items-center justify-start ">
                            {indicator}
                        </div>
                        <div className="flex h-full shrink-0 flex-col self-end">
                            <div
                                className="absolute right-0 top-0 flex cursor-pointer items-center justify-center rounded-bl-md p-1 text-white transition-all duration-300 hover:bg-gray-100 hover:text-gray-500"
                                onClick={onDelete}
                            >
                                <CloseIcon className="text-xl" />
                            </div>

                            <DropdownMenu>
                                <DropdownMenuTrigger>
                                    <div className="absolute bottom-0 right-0 mt-10 flex cursor-pointer items-center justify-center rounded-tl-md p-3 text-white transition-all duration-300 hover:bg-gray-100 hover:text-gray-500">
                                        <MenuOpenIcon className="relative -right-1  scale-150 transform" />
                                    </div>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent>
                                    <DropdownMenuLabel>Action</DropdownMenuLabel>
                                    <DropdownMenuSeparator />
                                    {menuItems.map((item, index) => {
                                        return (
                                            <DropdownMenuItem key={index} onClick={item.onClick}>
                                                <div className="flex w-full cursor-pointer items-center justify-between">
                                                    {item.label}
                                                    <div className="">{item.icon}</div>
                                                </div>
                                            </DropdownMenuItem>
                                        );
                                    })}
                                </DropdownMenuContent>
                            </DropdownMenu>
                        </div>
                    </div>
                </ContextMenuTrigger>
                <ContextMenuContent>
                    <ContextMenuLabel>{`Action ${action.type.charAt(0).toUpperCase()}${action.type
                        .slice(1)
                        .toLowerCase()}`}</ContextMenuLabel>
                    {menuItems.map((item, index) => {
                        return (
                            <ContextMenuItem onClick={item.onClick} key={index}>
                                <div className="flex w-full cursor-pointer items-center justify-between">
                                    {item.label}
                                    <div className="">{item.icon}</div>
                                </div>
                            </ContextMenuItem>
                        );
                    })}
                </ContextMenuContent>
            </ContextMenu>
        );
    } else {
        return (
            <div
                className="h-10 w-full rounded-md border border-dashed bg-blue-500 opacity-40 shadow"
                {...props}
                ref={ref}
                data-handler-id={handlerId}
            ></div>
        );
    }
};

BaseAction.propTypes = {
    icon: PropTypes.element.isRequired,
    children: PropTypes.element.isRequired,
    className: PropTypes.string,
    action: PropTypes.shape({
        id: PropTypes.number.isRequired,
        parentId: PropTypes.number,
        running: PropTypes.bool.isRequired,
        valid: PropTypes.bool.isRequired,
        type: PropTypes.string.isRequired,
    }).isRequired,
};

export default BaseAction;
