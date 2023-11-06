const PositionTypes = {
    TOP: 'top',
    BOTTOM: 'bottom',
    OUT: 'out',
    MIDDLE: 'middle',
};

const dragLocation = (ref, monitor) => {
    if (!ref.current) {
        return PositionTypes.OUT;
    }

    const hoverBoundingRect = ref.current.getBoundingClientRect();
    const toleranceDistance = 20;

    const clientOffset = monitor.getClientOffset();
    const top = hoverBoundingRect.top;
    const bottom = hoverBoundingRect.bottom;
    const currentY = clientOffset.y;

    const distFromTop = Math.abs(currentY - top);
    const distFromBottom = Math.abs(currentY - bottom);
    const innerTopBoundary = top + toleranceDistance;
    const innerBottomBoundary = bottom - toleranceDistance;

    if (distFromTop <= toleranceDistance) {
        return PositionTypes.TOP;
    }

    if (distFromBottom <= toleranceDistance) {
        return PositionTypes.BOTTOM;
    }

    if (currentY > innerTopBoundary && currentY < innerBottomBoundary) {
        return PositionTypes.MIDDLE;
    }

    return PositionTypes.OUT;
};

export { PositionTypes, dragLocation };
