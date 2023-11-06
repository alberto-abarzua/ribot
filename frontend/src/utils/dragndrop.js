const PositionTypes = {
    TOP: 'top',
    BOTTOM: 'bottom',
    OUT: 'out',
};

const dragLocation = (ref, monitor) => {
    if (!ref.current) {
        return PositionTypes.OUT;
    }

    const hoverBoundingRect = ref.current.getBoundingClientRect();

    // Get vertical middle of the element
    const hoverMiddleY = (hoverBoundingRect.bottom - hoverBoundingRect.top) / 2;

    // Determine mouse position
    const clientOffset = monitor.getClientOffset();

    // If getClientOffset is null, consider it as OUT
    if (!clientOffset) {
        return PositionTypes.OUT;
    }

    const hoverClientY = clientOffset.y - hoverBoundingRect.top;
    const hoverClientX = clientOffset.x - hoverBoundingRect.left;

    // Check if the mouse is outside the element on either axis
    if (
        hoverClientX < 0 ||
        hoverClientX > hoverBoundingRect.right - hoverBoundingRect.left ||
        hoverClientY < 0 ||
        hoverClientY > hoverBoundingRect.bottom - hoverBoundingRect.top
    ) {
        return PositionTypes.OUT;
    }

    // Corrected logic for top and bottom checks
    if (hoverClientY < hoverMiddleY) {
        return PositionTypes.TOP;
    } else {
        return PositionTypes.BOTTOM;
    }
};

export { PositionTypes, dragLocation };
