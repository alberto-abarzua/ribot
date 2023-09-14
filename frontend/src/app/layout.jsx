import './globals.css';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });
import Providers from '@/components/general/providers/Providers';

export const metadata = {
    title: 'Robot Arm Controller',
    description: 'Control a robot arm with a web interface',
};
// eslint-disable-next-line react/prop-types
export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <Providers>
                <body className={inter.className}>{children}</body>
            </Providers>
        </html>
    );
}
