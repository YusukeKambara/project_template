VERSION := 0.0.2
IMAGE_NAME := helloworld
SERVICE_NAME := helloworld
PROJECT_NAME := develop

TOPIC_NAME := ticker-symbols
SERVICE_ACCOUNT := cloud-run-pubsub-invoker
SERVICE_ACCOUNT_NAME := "Cloud Run Pub/Sub Invoker"

$(eval REGION := $(shell gcloud config get-value compute/region))
$(eval PROJECT_ID := $(shell gcloud projects list --filter=$(PROJECT_NAME) --format="value(projectId)"))
$(eval PROJECT_NUMBER := $(shell gcloud projects list --filter=$(PROJECT_NAME) --format="value(projectNumber)"))

.PHONY: build, deploy

# Common commands
build:
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/$(IMAGE_NAME):$(VERSION) \
						 --project $(PROJECT_ID)

deploy:
	gcloud run deploy $(SERVICE_NAME) --image gcr.io/$(PROJECT_ID)/$(IMAGE_NAME):$(VERSION) \
									--platform managed \
									--allow-unauthenticated \
									--set-env-vars=TARGET=test \
									--region $(REGION) \
									--project $(PROJECT_ID)

#
# ref: https://cloud.google.com/run/docs/triggering/pubsub-push?hl=ja#run_pubsub_handler-python
#
bind_to_pubsub:
	@echo "################################################"
	@echo [Topic Existence Check]
	@echo "################################################"
	$(eval CMD_RESULT := $(shell gcloud pubsub topics list --format="flattened" --filter="name=projects/$(PROJECT_ID)/topics/$(TOPIC_NAME)"))
	@if test "$(CMD_RESULT)" = ""; then \
		gcloud pubsub topics create $(TOPIC_NAME); \
	else \
		echo "$(TOPIC_NAME)" already exists; \
	fi

	@echo "################################################"
	@echo [Service-Account Existence Check]
	@echo "################################################"
	$(eval CMD_RESULT := $(shell gcloud iam service-accounts list --format="flattened" --filter="name=projects/$(PROJECT_ID)/serviceAccounts/$(SERVICE_ACCOUNT)@$(PROJECT_ID).iam.gserviceaccount.com"))
	@if test "$(CMD_RESULT)" = ""; then \
		gcloud iam service-accounts create $(SERVICE_ACCOUNT) --display-name $(SERVICE_ACCOUNT_NAME); \
	else \
		echo "$(SERVICE_ACCOUNT)" already exists; \
	fi

	@echo "################################################"
	@echo [Updated IAM policy]
	@echo "################################################"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member=serviceAccount:service-$(PROJECT_NUMBER)@gcp-sa-pubsub.iam.gserviceaccount.com \
		--role=roles/iam.serviceAccountTokenCreator

	@echo "################################################"
	@echo [Create subscription for call the cloud run]
	@echo "################################################"
	$(eval SERVICE_URL := $(shell gcloud run services list --platform managed --filter="metadata.name=$(SERVICE_NAME)" --format="value(status.url)"))
	gcloud pubsub subscriptions create $(SERVICE_NAME) --topic $(TOPIC_NAME) \
		--push-endpoint=$(SERVICE_URL)/ \
		--push-auth-service-account=$(SERVICE_ACCOUNT)@$(PROJECT_ID).iam.gserviceaccount.com

	@echo "################################################"
	@echo [Test Publish]
	@echo "################################################"
	gcloud pubsub topics publish $(TOPIC_NAME) --message "hello"