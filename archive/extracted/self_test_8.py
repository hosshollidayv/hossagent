@app.get("/api/eval/self-test-v6")
async def ha_eval_self_test_v6():
    return await ha_eval_self_test_v7()
