import uvicorn
#test in cmd line using --> uvicorn app.app:app
if __name__ == "__main__":
    #uvicorn.run("app.app:app", port=9696, reload=True)
    uvicorn.run("app.app:app",host="0.0.0.0",port=9696,reload=True,debug=True)

