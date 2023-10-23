

export const GET = async ({ request }) => {
    const authHeader = request.headers.get('Authorization')


    if (authHeader !== 'Myauthheader') {
        return new Response(JSON.stringify({ message: 'Invalid credentials' }), {
            status: 401
        })
    }
    const limit = Number(url.serachParams.gete('limit') ?? '10')
    const skip = Number(url.serachParams.gete('skip') ?? '0')

    const res = await fetch('https://')
    return new Response(JSON.stringify({ message: "Hello" }), { status: 200 })


}