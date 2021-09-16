import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet,
  Dimensions,
  View,
  Text,
  Button,
  Platform,
  Image,
  TouchableOpacity,
  AppRegistry,
  Alert
} from 'react-native';
import { Camera } from 'expo-camera';
import { AntDesign, MaterialIcons } from '@expo/vector-icons';
import * as MediaLibrary from 'expo-media-library';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer, useNavigation} from '@react-navigation/native';
import * as ImagePicker from 'expo-image-picker';
import AWS, { S3 } from 'aws-sdk';
import {RNS3} from 'react-native-aws3';

const WINDOW_HEIGHT = Dimensions.get('window').height;
const CAPTURE_SIZE = Math.floor(WINDOW_HEIGHT * 0.08);

var IMG_URI;

export default function App() {
  const [hasPermission, setHasPermission] = useState(null);


  useEffect(() => {
    (async () => {
      if (Platform.OS !== 'web') {
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (status !== 'granted') {
          alert('Sorry, we need camera roll permissions to make this work!');
        }
      }
    })();
  }, [])

  useEffect(() => {
    onHandlePermission();
  }, []);

  const onHandlePermission = async () => {
    const { status } = await Camera.requestPermissionsAsync();
    setHasPermission(status === 'granted');
  };

  if (hasPermission === null) {
    return <View />;
  }
  if (hasPermission === false) {
    return <Text style={styles.text}>No access to camera</Text>;
  }


  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'Home' }}
        />
        <Stack.Screen name="Cam" component={Cam} />
        <Stack.Screen name="Photos" component={Photos} />

      </Stack.Navigator>
    </NavigationContainer>
    );
  }



  function Cam({ navigation }) {
    const [cameraType, setCameraType] = useState(Camera.Constants.Type.back);
    const [isPreview, setIsPreview] = useState(false);
    const [isCameraReady, setIsCameraReady] = useState(false);
    const cameraRef = useRef();
    

    const onCameraReady = () => {
      setIsCameraReady(true);
    };

    const switchCamera = () => {
      if (isPreview) {
        return;
      }
      setCameraType(prevCameraType =>
        prevCameraType === Camera.Constants.Type.back
          ? Camera.Constants.Type.front
          : Camera.Constants.Type.back
      );
    };

    const onSnap = async () => {
      if (cameraRef.current) {
        const options = { quality: 0.7, base64: true };
        const data = await cameraRef.current.takePictureAsync(options);
        const source = data.base64;

        var TakenPhotoUri = data.uri
        console.log(TakenPhotoUri)
      
        MediaLibrary.saveToLibraryAsync(TakenPhotoUri)

        Alert.alert(
          "Image Taken, Go Home to Upload",
          "Succesfully Taken Image"
          [
            {
              text: "Go back",
              onPress: () => navigation.navigate('Home')
            },
            { text: "OK", onPress: () => console.log("OK Pressed")}
          ],
          { cancelable: true }
        );


      }
    };



    const cancelPreview = async () => {
      await cameraRef.current.resumePreview();
      setIsPreview(false);
    };

    return (
      <View style={styles.container}>
        <Camera
          ref={cameraRef}
          style={styles.container}
          type={cameraType}
          onCameraReady={onCameraReady}
          useCamera2Api={true}
        />
        <View style={styles.container}>
          {isPreview && (
            <TouchableOpacity
              onPress={cancelPreview}
              style={styles.closeButton}
              activeOpacity={0.7}
            >
              <AntDesign name='close' size={32} color='#fff' />
            </TouchableOpacity>
          )}
          {!isPreview && (
            <View style={styles.bottomButtonsContainer}>
              <TouchableOpacity disabled={!isCameraReady} onPress={switchCamera}>
                <MaterialIcons name='flip-camera-ios' size={28} color='white' />
              </TouchableOpacity>
              <TouchableOpacity
                activeOpacity={0.7}
                disabled={!isCameraReady}
                onPress={onSnap}
                style={styles.capture}
              />
            </View>
          )}
        </View>
      </View>
    );
}


function HomeScreen({ navigation }) {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center'}}>
      <Text style={{ fontSize: 20 , textAlign: 'center', padding: 10}}>
        Welcome! Please select the following to take a picture of your card or to select an existing picture
      </Text>
      <Button
        title="Go to Camera"
        onPress={() => navigation.navigate('Cam')}
      />
      <Button
        title="Select a photo"
        onPress={() => navigation.navigate('Photos')}
      />
    </View>
  );
}

function Photos({ navigation }) {
  const [image, setImage] = useState(null);

    const pickImage = async () => {
      let result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.All,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      IMG_URI = result.uri;

      console.log(result);
  
      if (!result.cancelled) {
        setImage(result.uri);
      }
    };
  
    async function UploadToS3() {
      const rndInt = Math.floor(Math.random() * 1839718) + 1;
      const randInt = parseInt(rndInt);
      console.log(randInt)
      const file = {
          uri: IMG_URI,
          name: ("image.png" + randInt),
          type: "image/png"
        }
      
        const options = {
          keyPrefix: "myuploads/",
          bucket: "vax-scan",
          region: "us-east-2",
          accessKey: "ACCESSKEY",
          secretKey: "SECRETACCESSKEY",
          successActionStatus: 201
        }
      try{
        const response = await RNS3.put(file, options)
        if (response.status === 201){
          console.log("Success: ", response.body)
        }
        else {
          console.log("Failed to upload image to S3: ", reponse)
        }
      }
      catch(error) {
        console.log(error)
      }
    }
  
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <Button title="Pick an image from camera roll, THEN press Upload Photo" onPress={pickImage} />
        <Button title="Upload photo" onPress={UploadToS3} />
        {image && <Image source={{ uri: image }} style={{ width: 300, height: 300 }} />}
      </View>
    );
}

const Stack = createNativeStackNavigator();

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject
  },
  text: {
    color: '#fff'
  },
  bottomButtonsContainer: {
    position: 'absolute',
    flexDirection: 'row',
    bottom: 28,
    width: '100%',
    alignItems: 'center',
    justifyContent: 'center'
  },
  closeButton: {
    position: 'absolute',
    top: 35,
    right: 20,
    height: 50,
    width: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#5A45FF',
    opacity: 0.7
  },
  capture: {
    backgroundColor: '#5A45FF',
    borderRadius: 5,
    height: CAPTURE_SIZE,
    width: CAPTURE_SIZE,
    borderRadius: Math.floor(CAPTURE_SIZE / 2),
    marginBottom: 28,
    marginHorizontal: 30
  }
});
