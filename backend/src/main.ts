import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import { useContainer } from 'class-validator';
import { DataModule } from './data/data.module';

async function bootstrap() {
	const app = await NestFactory.create(AppModule);
	app.useGlobalPipes(new ValidationPipe({}));

	useContainer(app.select(DataModule), { fallbackOnErrors: true });

	await app.listen(3000);
	console.info(`Application is running on: ${await app.getUrl()}`);
}
bootstrap();
