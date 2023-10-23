

export const GET = async ({ request }) => {
    const authHeader = request.headers.get('Authorization')


    if (authHeader !== 'Myauthheader') {
        return new Response(JSON.stringify({ message: 'Invalid credentials' }), {
            status: 401
        })
    }
    const limit = Number(url.serachParams.gete('limit') ?? '10')
    const skip = Number(url.serachParams.gete('skip') ?? '0')

    const res = await fetch('http://127.0.0.1:5000/posts?limit=${limit}&skip=${skip}')
    const data = await res.json()
    return new Response(JSON.stringify(data), { status: 200 })
}