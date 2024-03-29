import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import PropTypes from 'prop-types';

const TutorialCard = ({ title, description, children, className }) => {
    return (
        <Card className={`w-full shadow-lg ${className}`}>
            <CardHeader>
                <CardTitle>{title}</CardTitle>
                <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent className=" flex flex-col gap-y-2">{children}</CardContent>
        </Card>
    );
};

TutorialCard.propTypes = {
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    children: PropTypes.node.isRequired,
    className: PropTypes.string,
};

export default TutorialCard;
