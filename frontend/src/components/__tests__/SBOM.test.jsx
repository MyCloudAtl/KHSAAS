// FILE: frontend/src/components/SBOM.test.jsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import axios from 'axios';
import SBOM from './SBOM';
import { jest, describe, beforeEach, test, expect } from '@jest/globals';

jest.mock('axios');

describe('SBOM Component', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('fetches and displays SBOM data successfully', async () => {
        const mockResponse = {
            data: {
                sbomData: [{ softwareVersion: '1.0', dependency: 'dependency1', vulnerability: 'vulnerability1' }],
                recData: [{ softwareVersion: '1.1' }],
            },
        };
        axios.get.mockResolvedValueOnce(mockResponse);

        render(<SBOM />);

        fireEvent.change(screen.getByPlaceholderText('Enter product name'), { target: { value: 'TestProduct' } });
        fireEvent.click(screen.getByText('Get SBOM Data'));

        await waitFor(() => expect(axios.get).toHaveBeenCalledTimes(1));
        await waitFor(() => expect(screen.getByText('SBOM Data for TestProduct')).toBeInTheDocument());
        expect(screen.getByText('Software Version: 1.0')).toBeInTheDocument();
        expect(screen.getByText('Dependency On: dependency1')).toBeInTheDocument();
        expect(screen.getByText('Vulnerability: vulnerability1')).toBeInTheDocument();
        expect(screen.getByText('Safe TestProduct Versions')).toBeInTheDocument();
        expect(screen.getByText('Recommended Version: 1.1')).toBeInTheDocument();
    });

    test('displays error message on fetch failure', async () => {
        axios.get.mockRejectedValueOnce(new Error('Failed to fetch SBOM data.'));

        render(<SBOM />);

        fireEvent.change(screen.getByPlaceholderText('Enter product name'), { target: { value: 'TestProduct' } });
        fireEvent.click(screen.getByText('Get SBOM Data'));

        await waitFor(() => expect(axios.get).toHaveBeenCalledTimes(1));
        await waitFor(() => expect(screen.getByText('Failed to fetch SBOM data.')).toBeInTheDocument());
    });

    test('does not submit form without product name', async () => {
        render(<SBOM />);

        fireEvent.click(screen.getByText('Get SBOM Data'));

        await waitFor(() => expect(axios.get).toHaveBeenCalledTimes(0));
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
});