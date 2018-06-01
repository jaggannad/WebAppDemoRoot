import requests, datetime, json
from flask import Flask, render_template, redirect, flash, request, url_for, session, jsonify
from google.appengine.ext import ndb