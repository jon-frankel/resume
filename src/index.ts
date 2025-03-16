const {LAMBDA_URL} = process.env;

type ResponseBody = {
    visits: number;
    timestamp: string;
};

export const handler = async (): Promise<ResponseBody> => {
    const response = await fetch(LAMBDA_URL);
    console.log('Response:', response);
    return await response.json();
};

// On load, fetch the number of visits from the server and display it
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const data = await handler();
        document.getElementById('visits').innerText = data.visits.toString();
    } catch (error) {
        console.log('Error fetching data:', error);
    }
});
