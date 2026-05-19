const LAMBDA_URL = process.env.LAMBDA_URL || '';

type ResponseBody = {
    visits: number;
    timestamp: number;
};

export const handler = async (): Promise<ResponseBody> => {
    const response = await fetch(LAMBDA_URL, {
        method: 'POST',
        body: JSON.stringify({})
    });
    return await response?.json();
};

// On load, fetch the number of visits from the server and display it
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const data = await handler();
        const visitsElement = document.getElementById('visits');
        visitsElement.innerText = data.visits.toString();
    } catch (error) {
        console.error('Error fetching data', error);
    }
});
