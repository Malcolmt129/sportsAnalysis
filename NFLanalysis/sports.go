package main

import(

	"fmt"
	"net/http"
	"io"
	"os"
	"log"	
	"github.com/joho/godotenv"
)


type Environment struct {
	api_key string
}



func loadEnvironment() (*Environment, error) {
	err := godotenv.Load()

	if err != nil {
		log.Fatalf("Error loading .env file...")
		return nil, fmt.Errorf("Error loading .env file: ", err)
	}


	apiKey := os.Getenv("API_KEY")


	environment := &Environment {
		api_key: apiKey,
	}


	return environment, nil 
}

/*
	This function makes a call to rapidapi NFL data and then writes then
	contents of that request to a file output/nfl_team_data. This should 
	be used later to manipulate because we can only make 100 requests and
	month

*/
func getAllNflTeams(env *Environment) {

	url := "https://nfl-api-data.p.rapidapi.com/nfl-team-listing/v1/data"
	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("x-rapidapi-key", env.api_key)
	req.Header.Add("x-rapidapi-host", "nfl-api-data.p.rapidapi.com")

	res, err := http.DefaultClient.Do(req)

	if err != nil {
		log.Println("Error: ", err)
		return
	}


	defer res.Body.Close()
	body, err := io.ReadAll(res.Body)

	if err != nil {
		log.Println("Error reading response body: ", err)
		return //In go you need to handle errors explicitly instead of throwing errors
			   // thats why you see return statements at the end of every if statement
	}


	//Save the response body to a file
	file, err := os.Create("output/nfl_team_data.json")
	if err != nil {
		log.Println("Error creating file: ", err)
		return
	}


	defer file.Close()

	_, err = file.Write(body)
	
	if err != nil {
		log.Println("Error writing to file: ", err)
		return
	}



	fmt.Println("Response saved to nfl_team_data.json")
}

//Not finished yet
func getNFLPlayerIDs (env *Environment) {

	url := "https://nfl-api-data.p.rapidapi.com/nfl-player-info/v1/data"
	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("x-rapidapi-key", env.api_key) //need to protect this key before I make a github repo
	req.Header.Add("x-rapidapi-host", "nfl-api-data.p.rapidapi.com")

	res, err := http.DefaultClient.Do(req)

	if err != nil {
		log.Println("Error: ", err)
		return
	}


	defer res.Body.Close()
	body, err := io.ReadAll(res.Body)

	if err != nil {
		log.Println("Error reading response body: ", err)
		return //In go you need to handle errors explicitly instead of throwing errors
			   // thats why you see return statements at the end of every if statement
	}


	//Save the response body to a file
	file, err := os.Create("output/nfl_team_data.json")
	if err != nil {
		log.Println("Error creating file: ", err)
		return
	}


	defer file.Close()

	_, err = file.Write(body)
	
	if err != nil {
		log.Println("Error writing to file: ", err)
		return
	}



	fmt.Println("Response saved to nfl_team_data.json")
}

func main () {
	env, err := loadEnvironment() 
	
	if err != nil {
		log.Fatalf("Error loading .env file: %v", err)
	}
}

