import PropTypes from 'prop-types';

const PrimaryButton = ({ onClick, className, ...props }) => {
    return (
        <button
            onClick={onClick}
            className={`inline-flex h-10 w-full  items-center justify-center gap-2.5 rounded-md bg-emerald-700 p-2.5 font-normal text-white shadow transition duration-300 hover:bg-emerald-800 ${className}`}
            {...props}
        ></button>
    );
};

PrimaryButton.propTypes = {
    onClick: PropTypes.func.isRequired,
    className: PropTypes.string,
};

export default PrimaryButton;
