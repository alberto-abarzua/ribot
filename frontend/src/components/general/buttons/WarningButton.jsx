import PropTypes from 'prop-types';

const WarningButton = ({ onClick, className, ...props }) => {
    return (
        <button
            onClick={onClick}
            className={`inline-flex h-10 w-full items-center justify-center gap-2.5 rounded-md bg-red-400 p-2.5 text-white shadow transition duration-300 hover:bg-red-500 ${className}`}
            {...props}
        ></button>
    );
};

WarningButton.propTypes = {
    onClick: PropTypes.func.isRequired,
    className: PropTypes.string,
};

export default WarningButton;
